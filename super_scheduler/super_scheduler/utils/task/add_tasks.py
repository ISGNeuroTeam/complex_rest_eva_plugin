from django_celery_beat.models import PeriodicTask, IntervalSchedule
from typing import Optional, Set
import super_logger


def add_periodic_task(schedule,
                      func,
                      func_args: Optional[dict] = None,
                      name: Optional[str] = None,
                      **kwargs):

    if func_args is None:
        func_args = {}

    schedule = IntervalSchedule.objects.create(every=20, period=IntervalSchedule.SECONDS)
    task = PeriodicTask.objects.create(
        interval=schedule,
        name='test_logger123',
        task='super_scheduler.tasks.test_logger',
        args=func_args
    )

    # UPDATE TASK
    # task = PeriodicTask.objects.get(name="test_logger")  # if we suppose names are unique
    # task.args = func_args
    # task.save()

    return True
