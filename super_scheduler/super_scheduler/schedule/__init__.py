from .interval import IntervalDjangoSchedule, IntervalFormat
from .crontab import CrontabDjangoSchedule, CrontabFormat
from .solar import SolarDjangoSchedule, SolarFormat
from .сlocked import ClockedDjangoSchedule, ClockedFormat


SCHEDULES = {
    'interval': (IntervalDjangoSchedule, IntervalFormat),
    'crontab': (CrontabDjangoSchedule, CrontabFormat),
    'solar': (SolarDjangoSchedule, SolarFormat),
    'clocked': (ClockedDjangoSchedule, ClockedFormat),
}
