from rest.views import APIView
from rest.response import Response, status
from rest.permissions import AllowAny
from ..utils.interesting_fields_builder import InterestingFieldsBuilder
from ..utils.interesting_fields_loader import InterestingFieldsLoader
from typing import Dict
import uuid
import super_logger
import json


class InterestingFieldsView(APIView):

    permission_classes = (AllowAny,)
    http_method_names = ['get']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('dashboards')

    def __init__(self, mem_conf: Dict, static_conf: Dict, **kwargs):
        super().__init__(**kwargs)
        self.builder = InterestingFieldsBuilder()
        self.loader = InterestingFieldsLoader(mem_conf, static_conf)

    def get(self, request):
        cid = dict(request.GET).get('cid')
        if not cid:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        cid = cid[0]
        try:
            data = self.loader.load_data(cid)
            interesting_fields = self.builder.get_interesting_fields(data)
        except Exception as e:
            return Response(
                json.dumps({'status': 'failed', 'error': f'{e} cid {cid}'}, default=str),
                status.HTTP_400_BAD_REQUEST
            )
        return Response(
            json.dumps(interesting_fields),
            status.HTTP_200_OK
        )
