import os
from hashlib import blake2b

from rest_framework.exceptions import ParseError, APIException
from rest_framework.response import Response

from eva_plugin.base_handler import BaseHandler
from eva_plugin.settings import LOGS_PATH


class LogsHandler(BaseHandler):
    def __init__(self, *args, **kwargs):
        super(LogsHandler, self).__init__(*args, **kwargs)

        self.logs_path = LOGS_PATH

    def post(self, request):
        logs_text = self.data.get('log', None)
        if not logs_text:
            raise ParseError("params 'log' is needed")

        base_logs_dir = os.path.join(self.logs_path, 'cli_logs')
        if not os.path.exists(base_logs_dir):
            os.makedirs(base_logs_dir)

        h = blake2b(digest_size=4)
        h.update(self.token.encode())
        client_id = str(self.current_user) + '_' + h.hexdigest()

        log_file_path = os.path.join(base_logs_dir, client_id)
        try:
            with open(f'{log_file_path}.log', 'a+') as f:
                f.write(logs_text)
        except Exception as err:
            raise APIException(str(err))
        return Response({'status': 'success'})
