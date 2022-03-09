from rest.views import APIView
from rest.response import Response, status
from rest.permissions import AllowAny
from ..utils.timelines_builder import TimelinesBuilder
from ..utils.timelines_loader import TimelinesLoader
from typing import Dict
import uuid
import super_logger
import json


class TimelinesView(APIView):

    permission_classes = (AllowAny,)
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
