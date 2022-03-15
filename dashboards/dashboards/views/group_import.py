import json
import tarfile
import io
from datetime import datetime
from plugins.db_connector.connector_singleton import db
from rest.views import APIView
from rest.response import Response, status
from rest.permissions import IsAuthenticated
import uuid
import super_logger


class GroupImportView(APIView):
    """
    That handler allows to import groups, exported with GroupExportHandler.
    Or you can put your own 'eva.group' file with dirs named group_id
    with inner dashs json files.
    """

    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('dashboards')
    static_dir_name = 'storage'

    def post(self, request):
        files = request.FILES
        if not files or not files.get('body'):
            return Response(json.dumps({'status': 'no file in payload'}), status.HTTP_400_BAD_REQUEST)
        tar_file = files['body'][0]

        # wraps bytes to work with it like with file
        file_like_object = io.BytesIO(tar_file['body'])
        with tarfile.open(mode='r:gz', fileobj=file_like_object) as tar:
            inner_objects = tar.getnames()
            meta_list = [s for s in inner_objects if '_META' in s]
            dtn = datetime.now().strftime('%Y%m%d%H%M%S')

            for meta in meta_list:
                meta_data = tar.extractfile(meta)
                meta_dict = json.loads(meta_data.read())
                group_name = f"{meta_dict['name']}_imported_{dtn}"
                db.add_group(name=group_name,
                             color=meta_dict['color'])
                dashs = [s for s in inner_objects if s.startswith(f"{meta_dict['id']}/")
                         and '_META' not in s]
                for dash in dashs:
                    dash_name = dash.split('/', 1)[-1]
                    dash_data = tar.extractfile(dash)
                    db.add_dash(name=f'{dash_name}_imported_{dtn}',
                                body=dash_data.read().decode(),
                                groups=[group_name])
        return Response(json.dumps({'status': 'success'}))
