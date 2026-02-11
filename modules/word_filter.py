import logging
import re
from synapse.module_api import NOT_SPAM
from synapse.module_api.errors import Codes

logger = logging.getLogger(__name__)

class WordFilter:
    """
    Synapse spam checker module to filter and mask blocked words in messages.
    Blocked words are configured via the 'blocked_words' config key.
    """
    def __init__(self, config: dict, api):
        """
        Initialize the WordFilter module.
        Args:
            config (dict): Module configuration.
            api: Synapse module API instance.
        """
        self.api = api
        self.blocked_words = config.get("blocked_words", [])

        self.api.register_spam_checker_callbacks(
            check_event_for_spam=self.check_event_for_spam,
        )
        logger.info(f"*** {self.__class__.__name__} initalized | {self.blocked_words}***")

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
        Mask blocked words in message events.
        Args:
            event: Matrix event object.
        Returns:
            NOT_SPAM (always, but modifies event content if blocked words found)
        """
        logger.info(f"*** {self.__class__.__name__} | check_event_for_spam: {event} ***")

        if event.type != "m.room.message":
            return NOT_SPAM

        body = event.content.get("body", "")
        new_body = body
        modified = False

        for word in self.blocked_words:
            pattern = re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE)

            if pattern.search(new_body):
                stars = "*" * len(word)
                new_body = pattern.sub(stars, new_body)
                modified = True

        if modified:
            event.content["body"] = new_body
            logger.warning(f"{self.__class__.__name__} | BLOCKED: User {event.sender} sent a message containing blocked words. Original: {body}, Modified: {new_body}")

        return NOT_SPAM
