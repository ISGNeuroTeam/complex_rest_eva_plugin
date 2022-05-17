from django_celery_beat.models import PeriodicTask
from django_celery_beat.managers import ExtendedQuerySet

from plugins.super_scheduler.settings import app


def get_all_periodic_tasks() -> ExtendedQuerySet:
    """
    Return all periodic tasks from django model.
    """
    return PeriodicTask.objects.all()


def get_all_periodic_task_names() -> list:
    """
    Return all periodic task names from django model.
    """
    return [periodic_task.name for periodic_task in get_all_periodic_tasks()]


def get_all_tasks() -> set:
    """
    Return all task names.
    """
    return set(app.tasks.keys())
