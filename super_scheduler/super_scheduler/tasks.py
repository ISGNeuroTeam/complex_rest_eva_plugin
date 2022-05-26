from datetime import datetime, timedelta
from celery.schedules import crontab
import logging
import time

# from .settings import app
from core.celeryapp import app


log = logging.getLogger('super_scheduler.tasks')


@app.task()
def sample_task():
    log.info('Sample task done.')


@app.task()
def test_logger():
    log.info('Test log. Success task.')
    time.sleep(19)
