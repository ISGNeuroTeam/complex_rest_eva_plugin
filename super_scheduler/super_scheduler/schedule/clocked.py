from django_celery_beat.models import ClockedSchedule
from pydantic import validator

from datetime import datetime
from dateutil.parser import parse
from dateutil.tz import gettz

from core.settings.base import TIME_ZONE

from .base import BaseScheduleFormat


class ClockedFormat(BaseScheduleFormat):
    clocked_time: str

    @validator("clocked_time")
    def clocked_time_transformer(cls, value):
        # try:
        #     print(value)
        #     tzinfo = gettz(TIME_ZONE)
        #     value = parse(value, tzinfos={"PST": tzinfo, "PDT": tzinfo})
        #     print(value)
        # except Exception as e:
        #     raise ValueError(f"Not correct 'clocked_time' param. Error: {e}")
        # print(type(value))
        value = datetime.now()
        return value


ClockedDjangoSchedule = ClockedSchedule
