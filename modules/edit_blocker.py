import logging
from synapse.module_api import NOT_SPAM
from synapse.module_api.errors import Codes

logger = logging.getLogger(__name__)

class EditBlocker:
    """
    Synapse spam checker module to block message edits (m.replace) for users with power level under 50.
    """
    def __init__(self, config: dict, api):
        self.api = api
        self.required_power_level = config.get("required_power_level", 50)
        self.api.register_spam_checker_callbacks(
            check_event_for_spam=self.check_event_for_spam,
        )
        logger.info(f"*** {self.__class__.__name__} initialized | required_power_level={self.required_power_level} ***")

    @staticmethod
    def parse_config(config: dict) -> dict:
        return dict(config)

    async def check_event_for_spam(self, event):
        # Only block edits (m.room.message with m.relates_to.rel_type == "m.replace")
        if event.type != "m.room.message":
            return NOT_SPAM

        relates_to = event.content.get("m.relates_to", {})
        if relates_to.get("rel_type") != "m.replace":
            return NOT_SPAM

        user_id = event.sender
        is_admin = await self.api.is_user_admin(user_id)
        if is_admin:
            logger.info(f"*** {self.__class__.__name__}: User {user_id} is a server admin, allowing edit.")
            return NOT_SPAM

        room_id = event.room_id
        state_events = await self.api.get_room_state(room_id)
        power_levels = state_events.get(("m.room.power_levels", ""), {})
        content = power_levels.get("content", {})
        users = dict(content.get("users", {}))
        users_default = content.get("users_default", 0)
        user_level = users.get(user_id, users_default)

        # Allow if user is a system admin
        logger.info(f"EditBlocker: user_id={user_id}, users={users}, users_default={users_default}, user_level={user_level}, is_admin={is_admin}, power_levels_content={content}")
        if user_level < self.required_power_level:
            logger.warning(f"EditBlocker: Blocking edit from {user_id} in {room_id} (PL={user_level})")
            return (Codes.FORBIDDEN, {"error": f"You need PL {self.required_power_level} or to be a server admin to edit messages in this room."})

        return NOT_SPAM
