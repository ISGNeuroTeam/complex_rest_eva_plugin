import tarfile
import tempfile
from datetime import datetime
import os
from rest.views import APIView
from rest.response import Response, status
from rest.permissions import IsAuthenticated
import uuid
import super_logger
from plugins.db_connector.connector_singleton import db
from ..settings import STATIC_CONF
from ..utils.helper_functions import make_unique_name


class DashboardExportView(APIView):
    """
    View to export one or more dash object in '.json' format files.
    Json files returns in 'eva.dash' package with datetime-name.
    """

    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('dashboards')
    static_conf = STATIC_CONF
    static_dir_name = 'storage'

    def get(self, request):
        dash_ids = request.GET.get('ids', None)
        if not dash_ids:
            return Response("param 'ids' is needed", status.HTTP_400_BAD_REQUEST)
        dash_ids = dash_ids.split(',')
        dash_ids = [int(_) for _ in dash_ids]

        with tempfile.TemporaryDirectory() as tmp_dir:
            archive_name = f"{datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')}.eva.dash"
            _dirname = str(uuid.uuid4())
            _base_path = os.path.join(self.static_conf['static_path'], self.static_dir_name, _dirname)
            if not os.path.exists(_base_path):
                os.makedirs(_base_path)

            archive_path = os.path.join(_base_path, archive_name)
            archive = tarfile.open(archive_path, mode='x:gz')

            for did in dash_ids:
                try:
                    dash_data = db.get_dash_data(dash_id=did)
                    if not dash_data:
                        return Response(f'No dash with id={did}', status.HTTP_404_NOT_FOUND)
                except Exception as err:
                    return Response(str(err), status.HTTP_409_CONFLICT)

                path_template = os.path.join(tmp_dir, '{}.json')
                filename = make_unique_name(path_template, dash_data['name'])
                filepath = path_template.format(filename)

                if not os.path.exists(filepath):
                    with open(filepath, 'w+') as f:
                        f.write(dash_data['body'])

                archive.add(filepath, filename)
            archive.close()

        return Response(
            f'{self.static_dir_name}/{_dirname}/{archive_name}',
            status.HTTP_200_OK
        )
