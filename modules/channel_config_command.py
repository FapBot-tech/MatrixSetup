import logging
import asyncio
from synapse.module_api import ModuleApi, NOT_SPAM

logger = logging.getLogger(__name__)

DEFAULT_CINNY_POWER_LEVEL_TAGS = {
    "0": {"name": "Muted", "color": "#ff0000", "icon": {"key": "🤡"}},
    "10": {"name": "Member", "color": "#ffffff"},
    "50": {"name": "Moderator", "color": "#1fd81f"},
    "100": {"name": "Admin", "color": "#0088ff"},
    "999": {"name": "Final boss", "color": "#000000"}
}

class ChannelConfigCommand:
    """
    Synapse module to set in.cinny.room.power_level_tags state event and perform channel config actions when '!cinnytags' command is sent.
    Tags are configurable via the 'tags' key in homeserver.yaml.
    """
    def __init__(self, config: dict, api: ModuleApi):
        self.api = api
        self.tags = config.get("tags", DEFAULT_CINNY_POWER_LEVEL_TAGS)
        self.api.register_spam_checker_callbacks(
            check_event_for_spam=self.check_event_for_spam,
        )
        logger.info(f"*** {self.__class__.__name__} initialized with tags: {self.tags} ***")

    @staticmethod
    def parse_config(config: dict) -> dict:
        return dict(config)

    async def check_event_for_spam(self, event):
        # Only handle m.room.message events
        if event.type != "m.room.message":
            return NOT_SPAM

        user_id = event.sender
        is_admin = await self.api.is_user_admin(user_id)
        if not is_admin:
            logger.info(f"*** {self.__class__.__name__}: User {user_id} is not a server admin, they should not be doing this.")
            return NOT_SPAM

        body = event.content.get("body", "")
        if body.strip() == "!channelconfig":
            room_id = event.room_id

            # 1. Set Cinny power level tags
            event_dict = {
                "type": "in.cinny.room.power_level_tags",
                "room_id": room_id,
                "sender": user_id,
                "content": self.tags,
                "state_key": "",
            }
            try:
                result_event = await self.api.create_and_send_event_into_room(event_dict)
                logger.info(f"*** {self.__class__.__name__}: Sent power level tags for room {room_id} by {user_id}, event_id={getattr(result_event, 'event_id', None)}, dedup={getattr(result_event, 'dedup', None)}, content={result_event.content if hasattr(result_event, 'content') else result_event}")
                # Confirmation message
                await self.api.create_and_send_event_into_room({
                    "type": "m.room.message",
                    "room_id": room_id,
                    "sender": user_id,
                    "content": {
                        "msgtype": "m.notice",
                        "body": "Cinny power level tags have been set for this channel."
                    }
                })
            except Exception as e:
                logger.error(f"*** {self.__class__.__name__}: Failed to set tags for {room_id}: {e}")
                await self.api.create_and_send_event_into_room({
                    "type": "m.room.message",
                    "room_id": room_id,
                    "sender": user_id,
                    "content": {
                        "msgtype": "m.notice",
                        "body": f"Failed to set Cinny power level tags: {e}"
                    }
                })

            # 2. Make the room public to join
            try:
                dir_event = {
                    "type": "m.room.join_rules",
                    "room_id": room_id,
                    "sender": user_id,
                    "content": {"join_rule": "public"},
                    "state_key": "",
                }
                result_event = await self.api.create_and_send_event_into_room(dir_event)
                logger.info(f"*** {self.__class__.__name__}: Set room visibility for {room_id} || event_id={getattr(result_event, 'event_id', None)}, dedup={getattr(result_event, 'dedup', None)}, content={result_event.content if hasattr(result_event, 'content') else result_event}")
                await self.api.create_and_send_event_into_room({
                    "type": "m.room.message",
                    "room_id": room_id,
                    "sender": user_id,
                    "content": {
                        "msgtype": "m.notice",
                        "body": "Room join rule set to public."
                    }
                })
            except Exception as e:
                logger.error(f"*** {self.__class__.__name__}: Failed to set visibility for room {room_id}: {e}")
                await self.api.create_and_send_event_into_room({
                    "type": "m.room.message",
                    "room_id": room_id,
                    "sender": user_id,
                    "content": {
                        "msgtype": "m.notice",
                        "body": f"Failed to set room join rule: {e}"
                    }
                })

            # 3. Publish the room to the room directory
            try:
                result_event = await self.api.public_room_list_manager.add_room_to_public_room_list(room_id)
                logger.info(f"*** {self.__class__.__name__}: set_room_is_public({room_id}, True) called successfully.  || event_id={getattr(result_event, 'event_id', None)}, dedup={getattr(result_event, 'dedup', None)}, content={result_event.content if hasattr(result_event, 'content') else result_event}")
                await self.api.create_and_send_event_into_room({
                    "type": "m.room.message",
                    "room_id": room_id,
                    "sender": user_id,
                    "content": {
                        "msgtype": "m.notice",
                        "body": "Room published to the public directory."
                    }
                })
            except Exception as e:
                logger.error(f"*** {self.__class__.__name__}: Failed to publish room {room_id} to directory: {e}")
                await self.api.create_and_send_event_into_room({
                    "type": "m.room.message",
                    "room_id": room_id,
                    "sender": user_id,
                    "content": {
                        "msgtype": "m.notice",
                        "body": f"Failed to publish room to directory: {e}"
                    }
                })

            # 4. Set the history visibility to shared
            try:
                dir_event = {
                    "type": "m.room.history_visibility",
                    "room_id": room_id,
                    "sender": user_id,
                    "content": {"history_visibility": "shared"},
                    "state_key": "",
                }
                result_event = await self.api.create_and_send_event_into_room(dir_event)
                logger.info(f"*** {self.__class__.__name__}: Set history visibility for {room_id} || event_id={getattr(result_event, 'event_id', None)}, dedup={getattr(result_event, 'dedup', None)}, content={result_event.content if hasattr(result_event, 'content') else result_event}")
                await self.api.create_and_send_event_into_room({
                    "type": "m.room.message",
                    "room_id": room_id,
                    "sender": user_id,
                    "content": {
                        "msgtype": "m.notice",
                        "body": "Room history rule set to public for everyone."
                    }
                })
            except Exception as e:
                logger.error(f"*** {self.__class__.__name__}: Failed to set history setting for room {room_id}: {e}")
                await self.api.create_and_send_event_into_room({
                    "type": "m.room.message",
                    "room_id": room_id,
                    "sender": user_id,
                    "content": {
                        "msgtype": "m.notice",
                        "body": f"Failed to set room history setting: {e}"
                    }
                })
        return NOT_SPAM
