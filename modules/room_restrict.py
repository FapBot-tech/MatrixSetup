import logging
from synapse.api.errors import SynapseError
from synapse.module_api import NOT_SPAM
from synapse.module_api.errors import Codes

logger = logging.getLogger(__name__)

class RoomRestrictor:
    """
    Synapse third-party rules module to restrict room creation.
    Only admins can create group rooms; DMs are allowed for all users.
    """
    def __init__(self, config: dict, api):
        """
        Initialize the RoomRestrictor module.
        Args:
            config (dict): Module configuration.
            api: Synapse module API instance.
        """
        self.api = api

        # In 1.114.x, this is the correct way to get the full room config
        self.api.register_third_party_rules_callbacks(
            on_create_room=self.on_create_room,
        )

        self.api.register_spam_checker_callbacks(
            check_event_for_spam=self.check_event_for_spam,
        )
        logger.info(f"*** RoomRestrictor 1.114 (3rd Party Rules) active for***")

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

    async def on_create_room(self, requester, request_content, is_requester_admin):
        """
        Restrict room creation to admins, except for DMs.
        Args:
            requester: Requester object
            request_content: dict (The raw JSON body of the createRoom request)
            is_requester_admin: bool
        Raises:
            SynapseError: If non-admin tries to create a group room.
        """
        user_id = requester.user.to_string()

        # 1. Allow if the user is a global admin or your specific admin ID
        if is_requester_admin:
            return

        # 2. Check the raw dictionary for the 'is_direct' key
        # In Third Party Rules, 'request_content' is a standard Python dict
        is_direct = request_content.get("is_direct", False)

        if is_direct:
            logger.info(f"ALLOWING DM creation for {user_id}")
            return # Returning None allows the room

        # 3. Block everything else
        logger.warning(f"BLOCKING group room creation attempt by {user_id}")

        # Raising SynapseError is the ONLY way to stop the creation in this hook
        raise SynapseError(403, "Only admins can create group channels.")

    async def check_event_for_spam(self, event):
        """
        Mask blocked words in message events.
        Args:
            event: Matrix event object.
        Returns:
            NOT_SPAM (always, but modifies event content if blocked words found)
        """
        user_id = event.sender
        is_admin = await self.api.is_user_admin(user_id)
        if is_admin:
            logger.info(f"*** {self.__class__.__name__}: User {user_id} is a server admin, allowing content.")
            return NOT_SPAM

        if event.type != "m.room.join_rules":
            return NOT_SPAM

        return (Codes.FORBIDDEN, {"error": f"You are not allowed to change room visibility."})
