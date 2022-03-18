from rest.views import APIView
from rest.response import Response, status
from rest.permissions import IsAuthenticated
import uuid
import super_logger
from ..settings import STATIC_CONF
from ..utils.data_uploader import DataUploader


class SvgLoadView(APIView):

    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('dashboards')
    data_uploader = DataUploader()

    def post(self, request):
        svg_path = STATIC_CONF['static_path'] + 'svg'
        files = request.FILES
        if not files or not files.get('file'):
            return Response({"error": "no file in payload"}, status.HTTP_204_NO_CONTENT)
        try:
            self.data_uploader.save_binary(files, svg_path)
        except Exception as err:
            return Response({"error": str(err)}, status.HTTP_400_BAD_REQUEST)
        return Response({'status': 'ok'}, status.HTTP_200_OK)
