import logging
from synapse.module_api import NOT_SPAM

logger = logging.getLogger(__name__)

class DirectMessageInviteBlocker:
    """
    Synapse spam checker module to block inviting more than two users to DMs/private rooms.
    """
    def __init__(self, config: dict, api):
        """
        Initialize the DirectMessageInviteBlocker module.
        Args:
            config (dict): Module configuration.
            api: Synapse module API instance.
        """
        self.api = api
        self.api.register_spam_checker_callbacks(
            user_may_invite=self.user_may_invite,
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

    async def user_may_invite(self, inviter: str, invitee: str, room_id: str):
        """
        Block invites in DMs/private rooms if there are already two joined members.
        Args:
            inviter (str): User ID of the inviter.
            invitee (str): User ID of the invitee.
            room_id (str): Room ID.
        Returns:
            NOT_SPAM or error string.
        """
        logger.info(f"*** {self.__class__.__name__} | user_may_invite called: inviter={inviter}, invitee={invitee}, room_id={room_id} ***")
        try:
            state_events = await self.api.get_room_state(room_id)
            logger.info(f"*** {self.__class__.__name__} | user_may_invite: state_events keys: {list(state_events.keys())} ***")
        except Exception as e:
            logger.error(f"*** {self.__class__.__name__} | user_may_invite: Error fetching room state: {e}")
            return NOT_SPAM
        joined_members = [event for key, event in state_events.items()
                          if event.type == "m.room.member" and event.content.get("membership") == "join"]
        logger.info(f"*** {self.__class__.__name__} | user_may_invite: joined_members count: {len(joined_members)} ***")
        create_event = state_events.get(("m.room.create", ""))
        is_direct = create_event.content.get("is_direct", False) if create_event else False
        join_rules_event = state_events.get(("m.room.join_rules", ""))
        is_private = (join_rules_event.content.get("join_rule") == "invite") if join_rules_event else False
        logger.info(f"*** {self.__class__.__name__} | user_may_invite: is_direct={is_direct}, is_private={is_private} ***")
        if (is_direct or is_private) and len(joined_members) >= 2:
            logger.warning(f"*** {self.__class__.__name__} | user_may_invite: Blocking invite: would exceed 2 members in DM/private room {room_id}")
            return "Inviting more users to a direct/private message is not allowed."
        logger.info(f"*** {self.__class__.__name__} | user_may_invite: Allowing invite in room {room_id}")
        return NOT_SPAM
