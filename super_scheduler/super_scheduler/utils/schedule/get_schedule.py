from typing import Optional

from django_celery_beat.models import PeriodicTask

from plugins.super_scheduler.schedule import SCHEDULES


def get_all_schedules_subclasses() -> list:
    """
    Return all schedules in string format from django model merged into one list, unhashable types.
    """
    return [schedule_class.schedule for schedule_class in get_all_schedules()]


def get_all_schedules() -> set:
    """
    Return all schedules from django model merged into one set.
    """
    res_set = set()
    for schedule_class, schedule_format in SCHEDULES.values():
        res_set = res_set.union(set(schedule_class.objects.all()))

    return res_set


def get_schedule_name_by_schedule_class(schedule) -> Optional[str]:
    """
    Find schedule name by schedule class.

    :param schedule: schedule class from super_scheduler.schedule.SCHEDULES global variable
    :return: optional schedule name
    """
    # нужно что-то более оптимизированное и лаконичное
    # не удается получить доступ ко внутреннему классу Meta, у которого есть название типа расписания
    # При попытке обратиться к Meta: AttributeError: type object 'IntervalSchedule' has no attribute 'Meta'
    for key, (schedule_class, schedule_format) in SCHEDULES.items():
        if issubclass(type(schedule), schedule_class):
            return key
    return None


def get_schedule_name_from_task(task: PeriodicTask):
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
