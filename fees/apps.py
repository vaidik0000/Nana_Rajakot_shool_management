from django.apps import AppConfig
import logging


class FeesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fees'

    def ready(self):
        """
        Initialize app-specific configurations when the app is ready
        """
        # We'll keep the logger setup but remove the log message
        # logger = logging.getLogger('fees')
        # logger.info("Fees module initialized")
        pass
