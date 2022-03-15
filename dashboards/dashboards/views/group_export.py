import json
import tarfile
import tempfile
from datetime import datetime
from plugins.db_connector.connector_singleton import db
from rest.views import APIView
from rest.response import Response, status
from rest.permissions import IsAuthenticated
import uuid
import os
import super_logger
from ..settings import STATIC_CONF
from ..utils.helper_functions import make_unique_name


class GroupExportView(APIView):
    """
    View to export one or more group object with dashs in '.json' format files.
    Json files returns in 'eva.group' package with datetime-name.
    """

    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('dashboards')
    static_dir_name = 'storage'

    def get(self, request):
        group_ids = request.data.get('ids', None)
        if not group_ids:
            return Response("param 'ids' is needed", status.HTTP_400_BAD_REQUEST)
        group_ids = group_ids.split(',')
        group_ids = [int(_) for _ in group_ids]

        with tempfile.TemporaryDirectory() as tmp_dir:
            archive_name = f"{datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')}.eva.group"
            _dirname = str(uuid.uuid4())
            _base_path = os.path.join(STATIC_CONF['static_path'], self.static_dir_name, _dirname)
            if not os.path.exists(_base_path):
                os.makedirs(_base_path)

            archive_path = os.path.join(_base_path, archive_name)
            archive = tarfile.open(archive_path, mode='x:gz')

            for gid in group_ids:
                try:
                    dashs_data = db.get_dashs_data(group_id=gid)
                except Exception as err:
                    return Response(str(err), status.HTTP_409_CONFLICT)
                group_dir = os.path.join(tmp_dir, str(gid))
                if not os.path.exists(group_dir):
                    os.makedirs(group_dir)
                path_template = os.path.join(group_dir, '{}.json')

                for dash in dashs_data:
                    filename = make_unique_name(path_template, dash['name'])
                    filepath = path_template.format(filename)

                    if not os.path.exists(filepath):
                        with open(filepath, 'w+') as f:
                            f.write(dash['body'])
                    archive.add(filepath, os.path.join(str(gid), filename))

                # adds group metadata for future import
                meta_filemath = path_template.format('_META')
                with open(meta_filemath, 'w+') as f:
                    group_metadata = db.get_group_data(group_id=gid)
                    f.write(json.dumps(group_metadata))
                archive.add(meta_filemath, os.path.join(str(gid), '_META'))

            archive.close()
        return Response(f'{self.static_dir_name}/{_dirname}/{archive_name}', status.HTTP_200_OK)
