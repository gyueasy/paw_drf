from django.apps import AppConfig
from django.conf import settings
from django.core.cache import cache
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
import logging
import os

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler(timezone=timezone(settings.SCHEDULER_TIMEZONE))

class SingletonScheduler:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = BackgroundScheduler(timezone=timezone(settings.SCHEDULER_TIMEZONE))
        return cls._instance

class ReportsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reports'

    def ready(self):
        if settings.DEBUG:
            return
        
        if os.environ.get('RUN_MAIN') != 'true':
            return

        scheduler = SingletonScheduler.get_instance()
        if not cache.add('scheduler_lock', 'locked', timeout=60):
            logger.info("Scheduler is already running. Skipping initialization.")
            return
        
        logger.info("Initializing scheduler...")

        from .report_generator import generate_reports  # import here to avoid circular import

        scheduler.add_job(
            generate_reports,
            trigger=CronTrigger(hour="0,8,16", minute="30"),
            # trigger=CronTrigger(minute="*/3"),  # Test
            id="generate_reports",
            max_instances=1,
            replace_existing=True,
        )
        scheduler.start()
        logger.info("Scheduler started successfully")

