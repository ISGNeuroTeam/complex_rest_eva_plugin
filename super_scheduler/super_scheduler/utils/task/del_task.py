from django_celery_beat.models import PeriodicTask
from typing import Optional, Tuple
from pydantic import validator

from plugins.super_scheduler.utils.kwargs_parser import KwargsParser, BaseFormat as BaseTaskFormat
from plugins.super_scheduler.utils.task.get_task import get_all_periodic_task_names


class TaskDeleteFormat(BaseTaskFormat):

    @validator('name')
    def name_validator(cls, value: str) -> str:
        if value not in get_all_periodic_task_names():
            raise ValueError("Not exist periodic task name")
        return value


class DelPeriodicTask(KwargsParser):

    @classmethod
    def delete(cls, task_kwargs: dict) -> Tuple[bool, Optional[str]]:

        task_kwargs, msg = cls.parse_kwargs(task_kwargs, TaskDeleteFormat)
        if task_kwargs is None:
            return False, msg

        task = PeriodicTask.objects.get(
            **task_kwargs
        )
        task.delete()
        return True, None
