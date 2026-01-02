import logging
import re
from synapse.module_api import NOT_SPAM
from synapse.module_api.errors import Codes

logger = logging.getLogger(__name__)

class WordFilter:
    def __init__(self, config, api):
        self.api = api
        self.blocked_words = config.get("blocked_words", [])

        self.api.register_spam_checker_callbacks(
            check_event_for_spam=self.check_event_for_spam,
        )
        logger.info(f"*** {self.__class__.__name__} initalized | {self.blocked_words}***")

    @staticmethod
    def parse_config(config):
        return config

    async def check_event_for_spam(self, event):
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
