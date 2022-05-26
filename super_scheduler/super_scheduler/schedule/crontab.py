from django_celery_beat.models import CrontabSchedule
from datetime import datetime
from celery import Celery

from .base import BaseScheduleFormat


class CrontabFormat(BaseScheduleFormat):
    minute: str = '*'
    hour: str = '*'
    day_of_week: str = '*'
    day_of_month: str = '*'
    month_of_year: str = '*'
    # nowfun: datetime
    # app: Celery  # Can't use this type; error


CrontabDjangoSchedule = CrontabSchedule
