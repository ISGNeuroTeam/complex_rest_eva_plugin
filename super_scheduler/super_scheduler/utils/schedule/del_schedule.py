from django_celery_beat.models import PeriodicTask
from typing import Optional, Tuple
from pydantic import validator

from core.celeryapp import app

from plugins.super_scheduler.schedule import SCHEDULES, schedule_name2class
from plugins.super_scheduler.utils.kwargs_parser import KwargsParser, BaseFormat as BaseTaskFormat
from plugins.super_scheduler.utils.schedule.get_schedule import get_all_schedules_subclasses


class ScheduleDeleteFormat(BaseTaskFormat):
    schedule_subclass: any

    @validator('name', allow_reuse=True)
    def name_validator(cls, value: str) -> str:
        if value not in SCHEDULES:
            raise ValueError(f"Not exist schedule with name: {value}")
        return value

    @validator('schedule_subclass')
    def schedule_subclass_exist(cls, value):
        if value not in get_all_schedules_subclasses():
            raise ValueError(f"Not exist schedule with schedule_subclass: {value}")
        return value


class DelSchedule(KwargsParser):

    @classmethod
    def _get_schedule(cls, schedule_kwargs: dict):
        """
        Get schedule by dict with keys 'name' and 'schedule_subclass'.

        :param schedule_kwargs: dict with keys 'name' and 'schedule_subclass'
        :return: schedule class (django model)
        """
        schedule_name = schedule_kwargs['name']
        schedule_subclass = schedule_kwargs['schedule_subclass']
        return schedule_name2class(schedule_name).from_schedule(schedule_subclass)

    @classmethod
    def delete(cls, schedule_kwargs: dict) -> Tuple[bool, Optional[str]]:
        """
        Delete schedule.

        :param schedule_kwargs:
        :return:
        """

        schedule_kwargs, msg = cls.parse_kwargs(schedule_kwargs, ScheduleDeleteFormat)
        if schedule_kwargs is None:
            return False, msg

        schedule = cls._get_schedule(schedule_kwargs)
        schedule.delete()
        return True, None

