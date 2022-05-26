from django_celery_beat.models import PeriodicTask, ClockedSchedule
from typing import Optional, Tuple
from pydantic import validator

from plugins.super_scheduler.utils.kwargs_parser import KwargsParser, BaseFormat as BaseTaskFormat
from plugins.super_scheduler.utils.task.get_task import get_all_periodic_task_names, get_all_periodic_tasks
from plugins.super_scheduler.schedule import SCHEDULES, schedule_name2class
from plugins.super_scheduler.utils.schedule.del_schedule import DelSchedule


class TaskDeleteFormat(BaseTaskFormat):

    @validator('name', allow_reuse=True)
    def name_validator(cls, value: str) -> str:
        if value not in get_all_periodic_task_names():
            raise ValueError("Not exist periodic task name")
        return value


class DelPeriodicTask(KwargsParser):

    @classmethod
    def _check_schedule_in_another_tasks(cls, task: PeriodicTask) -> bool:
        """

        :param task:
        :return:
        """
        for task_iter in get_all_periodic_tasks():
            if task_iter.name != task.name and task_iter.schedule == task.schedule:
                return True
        return False

    @classmethod
    def _get_schedule_name_from_task(cls, task: PeriodicTask):
        """

        :param task: PeriodicTask object
        :return: schedule class (django model)
        """
        # similar to PeriodicTask.schedule because this method returns string interpretation, not schedule classes!
        if task.crontab:
            schedule_name = 'crontab'
        elif task.interval:
            schedule_name = 'interval'
        elif task.solar:
            schedule_name = 'solar'
        elif task.clocked:
            schedule_name = 'clocked'
        else:
            raise ValueError("No schedule in 'task'. Check 'SCHEDULES' variable and 'PeriodicTask.schedule' method.")

        assert schedule_name in SCHEDULES, ValueError(f"{schedule_name} not in 'SCHEDULES'")

        return schedule_name

    @classmethod
    def _delete_unused_schedule(cls, task: PeriodicTask) -> Tuple[bool, Optional[str]]:
        """
        Delete unused schedule in another tasks.

        :param task: PeriodicTask object
        :returns:
        """
        name = cls._get_schedule_name_from_task(task)
        schedule_subclass = task.schedule
        status_schedule, msg = DelSchedule.delete({'name': name, 'schedule_subclass': schedule_subclass})
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

        if not cls._check_schedule_in_another_tasks(task):
            # task will be delete if delete schedule
            return cls._delete_unused_schedule(task)
        else:
            task.delete()
            return True, None
