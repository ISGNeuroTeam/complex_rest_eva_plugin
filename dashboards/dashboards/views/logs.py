from rest.views import APIView
from rest.response import Response, status
from rest.permissions import IsAuthenticated
import uuid
import super_logger
from ..settings import LOGS_PATH
from ..utils.data_uploader import data_uploader


class LogsView(APIView):

    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('dashboards')
    logs_path = LOGS_PATH

    def post(self, request):
        logs_text = request.data.get('log', None)
        token = request.META['HTTP_AUTHORIZATION']
        if not logs_text:
            return Response("params 'log' is needed", status.HTTP_400_BAD_REQUEST)
        try:
            data_uploader.save_logs(token, request.user.id, LOGS_PATH, logs_text)
        except Exception as err:
            return Response(str(err), status.HTTP_400_BAD_REQUEST)
        return Response({'status': 'success'}, status.HTTP_200_OK)
