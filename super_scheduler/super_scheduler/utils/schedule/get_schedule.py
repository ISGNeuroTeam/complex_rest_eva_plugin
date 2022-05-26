from django_celery_beat.models import PeriodicTask, ClockedSchedule
from django_celery_beat.managers import ExtendedQuerySet

from core.celeryapp import app

from plugins.super_scheduler.schedule import SCHEDULES


def get_all_schedules_subclasses() -> set:
    """
    Return all schedules in string format from django model merged into one set.
    """
    res_set = set()
    for schedule_class in get_all_schedules():
        res_set.add(schedule_class.schedule)

    return res_set


def get_all_schedules() -> set:
    """
    Return all schedules from django model merged into one set.
    """
    res_set = set()
    for schedule_class, schedule_format in SCHEDULES.values():
        res_set = res_set.union(set(schedule_class.objects.all()))

    return res_set


