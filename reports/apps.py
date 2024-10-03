from django.apps import AppConfig
from django.conf import settings
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
import logging

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler(timezone=timezone(settings.SCHEDULER_TIMEZONE))

class ReportsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reports'

    def ready(self):
        if settings.DEBUG:
            return

        from .report_generator import generate_reports  # import here to avoid circular import

        scheduler.add_job(
            generate_reports,
            # trigger=CronTrigger(hour="0,8,16", minute="30"),
            trigger=CronTrigger(minute="*/3"),  # Test
            id="generate_reports",
            max_instances=1,
            replace_existing=True,
        )
        scheduler.start()
        logger.info("Scheduler started")

