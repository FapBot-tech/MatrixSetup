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

class CinnyPowerLevelTags:
    """
    Synapse module to set in.cinny.room.power_level_tags state event when '!cinnytags' command is sent.
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
        if body.strip() == "!cinnytags":
            room_id = event.room_id
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
                # Mark the command message as spam so it is not shown to users
                return (403, {"error": "Spam command message hidden."})
            except Exception as e:
                logger.error(f"*** {self.__class__.__name__}: Failed to set tags for {room_id}: {e}")

        return NOT_SPAM
