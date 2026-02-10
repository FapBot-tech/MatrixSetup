import logging
import magic
from synapse.module_api import NOT_SPAM
from synapse.module_api.errors import Codes

logger = logging.getLogger(__name__)

class PrivateMessageFileBlocker:
    def __init__(self, config, api):
        self.api = api

        self.mime_scanner = magic.Magic(mime=True)

        self.api.register_third_party_rules_callbacks(
            check_event_allowed=self.check_event_allowed,
        )
        logger.info(f"*** {self.__class__.__name__} initalized***")

    @staticmethod
    def parse_config(config):
        return config

    async def check_event_allowed(self, event, state_events):
        # 1. Only filter message events
        if event.type != "m.room.message":
            return True, None

        # 2. Check for media msgtypes
        file_msgtypes = ["m.image", "m.video", "m.audio", "m.file"]
        msgtype = event.content.get("msgtype")

        if msgtype not in file_msgtypes:
            return True, None

        # 3. Identify room type from state_events
        # Get m.room.create to check for is_direct
        create_event = state_events.get(("m.room.create", ""))
        is_direct = create_event.content.get("is_direct", False) if create_event else False

        # Get m.room.join_rules to check for 'invite' (Private)
        join_rules_event = state_events.get(("m.room.join_rules", ""))
        is_private = (join_rules_event.content.get("join_rule") == "invite") if join_rules_event else False

        # 4. Block if it's a file in a DM or Private room
        if is_direct or is_private:
            logger.warning(f"BLOCKING file ({msgtype}) in room {event.room_id} from {event.sender} DIRECT: {is_direct} | PRIVATE: {is_private}")
            # check_event_allowed expects a boolean return
            return False, {"error": "File sharing is disabled in DMs and Private channels."}

        return True, None
