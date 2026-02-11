import logging
import magic
from synapse.module_api import NOT_SPAM
from synapse.module_api.errors import Codes

logger = logging.getLogger(__name__)

class FileTypeFilter:
    """
    Synapse spam checker module to restrict allowed media file types.
    Allowed types are configured via the 'allowed_types' config key.
    """
    def __init__(self, config: dict, api):
        """
        Initialize the FileTypeFilter module.
        Args:
            config (dict): Module configuration.
            api: Synapse module API instance.
        """
        self.api = api
        self.allowed_types = config.get("allowed_types", [
            'video/mp4', 'audio/mp3', 'image/jpeg', 'image/png', 'image/gif'
        ])
        self.mime_scanner = magic.Magic(mime=True)
        self.api.register_spam_checker_callbacks(
            check_media_file_for_spam=self.check_media_file_for_spam,
        )
        logger.info(f"*** {self.__class__.__name__} initialized | {self.allowed_types} ***")

    @staticmethod
    def parse_config(config: dict) -> dict:
        """
        Parse and validate the module config. Extend this for async validation if needed.
        Args:
            config (dict): Raw config.
        Returns:
            dict: Parsed config.
        """
        # Accept unknown keys for future compatibility
        return dict(config)

    async def check_media_file_for_spam(self, file_wrapper, file_info):
        """
        Check if a media file is allowed based on its MIME type.
        Args:
            file_wrapper: File wrapper object with 'path' attribute.
            file_info: File info object, may have 'thumbnail'.
        Returns:
            NOT_SPAM or (Codes.FORBIDDEN, {"error": ...})
        """
        thumbnail_data = getattr(file_info, "thumbnail", None)

        if thumbnail_data:
            logger.info(f"*** {self.__class__.__name__} | Thumbnail, no processing ***")
            return NOT_SPAM

        file_path = getattr(file_wrapper, "path", None)
        if not file_path:
            logger.info(f"*** {self.__class__.__name__} | No file path, no processing ***")
            return NOT_SPAM

        try:
            file_type = self.mime_scanner.from_file(file_path).lower()
        except Exception as e:
            logger.error(f"FileTypeFilter: Error sniffing file: {e}")
            file_type = "unknown/unknown"

        if file_type not in self.allowed_types:
            logger.warning(f"*** {self.__class__.__name__} | BLOCKING: {file_type} is not an allowed media type.")
            return (Codes.FORBIDDEN, {"error": f"File type '{file_type}' is forbidden."})

        return NOT_SPAM

