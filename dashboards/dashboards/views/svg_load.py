from rest.views import APIView
from rest.response import Response, status
from rest.permissions import IsAuthenticated
import uuid
import super_logger
import json
import os
from ..settings import STATIC_CONF


class SvgLoadView(APIView):

    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('dashboards')

    def post(self, request):
        svg_path = STATIC_CONF['static_path'] + 'svg'
        _file = request.FILES['file'][0]
        saving_full_path = os.path.join(svg_path, _file['filename'])
        if not os.path.exists(saving_full_path):
            with open(saving_full_path, 'wb') as f:
                f.write(_file['body'])
        return Response(json.dumps({'status': 'ok'}), status.HTTP_200_OK)
