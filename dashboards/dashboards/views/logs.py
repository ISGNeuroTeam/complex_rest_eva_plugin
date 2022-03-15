from rest.views import APIView
from rest.response import Response, status
from rest.permissions import IsAuthenticated
import uuid
import super_logger
import os
from hashlib import blake2b
import json
from ..settings import LOGS_PATH


class LogsView(APIView):

    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('dashboards')
    logs_path = LOGS_PATH

    def post(self, request):
        logs_text = request.POST.get('log', None)
        token = request.META['Authorization']
        token = token[token.find(' ') + 1:]  # remove 'Token ' from token
        if not logs_text:
            return Response("params 'log' is needed", status.HTTP_400_BAD_REQUEST)
        base_logs_dir = os.path.join(self.logs_path, 'cli_logs')
        if not os.path.exists(base_logs_dir):
            os.makedirs(base_logs_dir)
        h = blake2b(digest_size=4)
        h.update(token.encode())
        client_id = str(request.user.id) + '_' + h.hexdigest()

        log_file_path = os.path.join(base_logs_dir, client_id)

        try:
            with open(f'{log_file_path}.log', 'a+') as f:
                f.write(logs_text)
        except Exception as err:
            return Response(str(err), status.HTTP_405_METHOD_NOT_ALLOWED)
        return Response(json.dumps({'status': 'success'}), status.HTTP_200_OK)
