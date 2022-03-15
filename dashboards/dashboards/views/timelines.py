from rest.views import APIView
from rest.response import Response, status
from rest.permissions import IsAuthenticated
from ..utils.timelines_builder import TimelinesBuilder
from ..utils.timelines_loader import TimelinesLoader
from typing import Dict
import uuid
import super_logger
import json


class TimelinesView(APIView):
    """
    Returns a list of 4 timelines. Every timeline has 50 objects. One object is a pair (time, value) and represents
    a time interval.
    :time: - unix timestamp
    :value: - how many events happened during the time interval

    Timelines differ by their time interval:
    1st - 1 minute
    2nd - 1 hour
    3rd - 1 day
    4th - 1 month
    """

    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('dashboards')

    def __init__(self, mem_conf: Dict, static_conf: Dict, **kwargs):
        super().__init__(**kwargs)
        self.builder = TimelinesBuilder()
        self.loader = TimelinesLoader(mem_conf, static_conf, self.builder.BIGGEST_INTERVAL)

    def get(self, request):
        cid = dict(request.GET).get('cid')
        if not cid:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        cid = cid[0]
        try:
            data = self.loader.load_data(cid)
            timelines = self.builder.get_all_timelines(data)
        except Exception as e:
            return Response(
                json.dumps({'status': 'failed', 'error': f'{e} cid {cid}'}, default=str),
                status.HTTP_400_BAD_REQUEST
            )
        return Response(
            json.dumps(timelines),
            status.HTTP_200_OK
        )
