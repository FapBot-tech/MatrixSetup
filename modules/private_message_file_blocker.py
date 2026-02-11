import logging
import magic
from synapse.module_api import NOT_SPAM

logger = logging.getLogger(__name__)

class PrivateMessageFileBlocker:
    """
    Synapse spam checker module to block file/media sharing in DMs and private rooms.
    """
    def __init__(self, config: dict, api):
        """
        Initialize the PrivateMessageFileBlocker module.
        Args:
            config (dict): Module configuration.
            api: Synapse module API instance.
        """
        self.api = api
        self.mime_scanner = magic.Magic(mime=True)

        # Register using the recommended spam checker API
        self.api.register_spam_checker_callbacks(
            check_event_for_spam=self.check_event_for_spam,
        )
        logger.info(f"*** {self.__class__.__name__} initialized ***")

    @staticmethod
    def parse_config(config: dict) -> dict:
        """
        Parse and validate the module config. Extend for async validation if needed.
        Args:
            config (dict): Raw config.
        Returns:
            dict: Parsed config.
        """
        return dict(config)

    async def check_event_for_spam(self, event):
        """
        Block file/media messages in DMs and private rooms.
        Args:
            event: Matrix event object.
        Returns:
            NOT_SPAM or error string.
        """
        # 1. Only filter message events
        if event.type != "m.room.message":
            logger.info(f"*** {self.__class__.__name__} | Event isn't a message***")
            return NOT_SPAM

        # 2. Check for media msgtypes
        file_msgtypes = ["m.image", "m.video", "m.audio", "m.file"]
        msgtype = event.content.get("msgtype")

        if msgtype not in file_msgtypes:
            logger.info(f"*** {self.__class__.__name__} | Message is no attachment ***")
            return NOT_SPAM

        user_id = event.sender
        is_admin = await self.api.is_user_admin(user_id)
        if is_admin:
            logger.info(f"*** {self.__class__.__name__}: User {user_id} is a server admin, allowing file upload.")
            return NOT_SPAM

        state_events = await self.api.get_room_state(event.room_id)

        # Identify DM status via m.room.create
        create_event = state_events.get(("m.room.create", ""))
        is_direct = create_event.content.get("is_direct", False) if create_event else False

        # Identify Private status via m.room.join_rules
        join_rules_event = state_events.get(("m.room.join_rules", ""))
        is_private = (join_rules_event.content.get("join_rule") == "invite") if join_rules_event else False

        # 4. Block if match found
        if is_private or is_direct:
            logger.warning(f"*** {self.__class__.__name__} | Blocking media in private/DM room: {event.room_id}")
            return "File sharing is disabled in DMs and Private channels."

        return NOT_SPAM
