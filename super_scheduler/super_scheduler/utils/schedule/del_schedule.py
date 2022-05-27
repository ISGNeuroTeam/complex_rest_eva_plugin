from django_celery_beat.models import PeriodicTask
from typing import Optional, Tuple
from pydantic import validator

from core.celeryapp import app

from plugins.super_scheduler.schedule import SCHEDULES, schedule_name2class
from plugins.super_scheduler.utils.kwargs_parser import KwargsParser, BaseFormat as BaseTaskFormat
from plugins.super_scheduler.utils.schedule.get_schedule import get_all_schedules_subclasses
from plugins.super_scheduler.utils.schedule.add_schedule import AddSchedule


class ScheduleDeleteFormat(BaseTaskFormat):

    @validator('name', allow_reuse=True)
    def name_validator(cls, value: str) -> str:
        if value not in SCHEDULES:
            raise ValueError(f"Not exist schedule with name: {value}")
        return value


class DelSchedule(KwargsParser):

    @classmethod
    def delete_by_schedule_subclass(cls, schedule_name: str, schedule_subclass) -> Tuple[bool, Optional[str]]:
        """
        Delete schedule by schedule subclass.

        :param schedule_name:
        :param schedule_subclass:
        :return:
        """

        if schedule_name not in SCHEDULES:
            return False, f"Not exist schedule with name: {schedule_name}"

        if schedule_subclass not in get_all_schedules_subclasses():
            return False, f"Not exist schedule with schedule_subclass: {schedule_subclass}"

        schedule_name2class(schedule_name).from_schedule(schedule_subclass).delete()
        return True, None

    @classmethod
    def delete(cls, schedule_kwargs: dict) -> Tuple[bool, Optional[str]]:
        """
        Delete schedule by schedule kwargs.

        :param schedule_kwargs:
        :return:
        """

        schedule_kwargs, msg = cls.parse_kwargs(schedule_kwargs, ScheduleDeleteFormat)
        if schedule_kwargs is None:
            return False, msg

        schedule, msg = AddSchedule.create(schedule_kwargs)
        if schedule is None:
            return False, msg

        schedule.delete()
        return True, None

