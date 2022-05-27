from django_celery_beat.models import PeriodicTask
from typing import Optional, Tuple
from pydantic import validator

from plugins.super_scheduler.utils.kwargs_parser import KwargsParser, BaseFormat as BaseTaskFormat
from plugins.super_scheduler.utils.schedule.get_schedule import get_schedule_name_from_task
from plugins.super_scheduler.utils.task.get_task import get_all_periodic_task_names, get_all_periodic_tasks
from plugins.super_scheduler.utils.schedule.del_schedule import DelSchedule


class TaskDeleteFormat(BaseTaskFormat):

    @validator('name', allow_reuse=True)
    def name_validator(cls, value: str) -> str:
        if value not in get_all_periodic_task_names():
            raise ValueError("Not exist periodic task name")
        return value


def check_schedule_in_another_tasks(schedule_sublass, task_name: str = None) -> bool:
    """

    :param schedule_sublass:
    :param task_name:
    :return:
    """
    for task_iter in get_all_periodic_tasks():
        if (task_iter.schedule == schedule_sublass) and \
                ((task_name is None) or (task_name and task_iter.name != task_name)):
            return True
    return False


class DelPeriodicTask(KwargsParser):

    @classmethod
    def _delete_unused_schedule(cls, task: PeriodicTask) -> Tuple[bool, Optional[str]]:
        """
        Delete unused schedule in another tasks.

        :param task: PeriodicTask object
        :returns:
        """
        name = get_schedule_name_from_task(task)
        schedule_subclass = task.schedule
        status_schedule, msg = DelSchedule.delete_by_schedule_subclass(name, schedule_subclass)
        return status_schedule, msg

    @classmethod
    def delete(cls, task_kwargs: dict) -> Tuple[bool, Optional[str]]:
        """
        Delete periodic task with unused schedules.

        :param task_kwargs:
        :return:
        """

        task_kwargs, msg = cls.parse_kwargs(task_kwargs, TaskDeleteFormat)
        if task_kwargs is None:
            return False, msg

        task = PeriodicTask.objects.get(
            **task_kwargs
        )

        if not check_schedule_in_another_tasks(task.schedule, task.name):
            # task will be delete if delete schedule
            return cls._delete_unused_schedule(task)
        else:
            task.delete()
            return True, None
