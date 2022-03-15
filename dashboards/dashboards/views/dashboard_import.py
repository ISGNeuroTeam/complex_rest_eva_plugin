import tarfile
from datetime import datetime
import io
import json
from plugins.db_connector.connector_singleton import db
from rest.views import APIView
from rest.response import Response, status
from rest.permissions import IsAuthenticated
import uuid
import super_logger


class DashboardImportView(APIView):
    """
    View to import dashs, exported with DashExportHandler.
    Or you can put your own 'eva.dash' file with inner dashs json files.
    """

    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('dashboards')


    def post(self, request):
        # body = request.data
        # args = {}
        # files = {}

        # tornado.httputil.parse_body_arguments(self.request.headers['Content-Type'], body, args, files)
        group = request.data.get('group')
        files = request.FILES

        if not files or not files.get('body'):
            return Response(json.dumps({'status': 'no file in payload'}), status.HTTP_400_BAD_REQUEST)
        tar_file = files['body'][0]

        # wraps bytes to work with it like with file
        file_like_object = io.BytesIO(tar_file['body'])
        with tarfile.open(mode='r:gz', fileobj=file_like_object) as tar:
            dtn = datetime.now().strftime('%Y%m%d%H%M%S')
            for dash in tar.getmembers():
                try:
                    dash_data = tar.extractfile(dash)
                    db.add_dash(name=f'{dash.name}_imported_{dtn}',
                                     body=dash_data.read().decode(),
                                     groups=[group[0].decode()])
                except Exception as err:
                    return Response(str(err), status.HTTP_409_CONFLICT)
            return Response(json.dumps({'status': 'success'}), status.HTTP_200_OK)
