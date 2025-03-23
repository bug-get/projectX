from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        import accounts.signals
        logger.info("Сигналы из accounts.signals импортированы")