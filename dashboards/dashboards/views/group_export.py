from rest.views import APIView
from rest.response import Response, status
from rest.permissions import IsAuthenticated
import uuid
import super_logger
from ..settings import STATIC_CONF
from ..utils.data_uploader import data_uploader


class GroupExportView(APIView):
    """
    View to export one or more group object with dashs in '.json' format files.
    Json files returns in 'eva.group' package with datetime-name.
    """

    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('dashboards')

    def get(self, request):
        group_ids = request.GET.get('ids', None)
        if not group_ids:
            return Response("param 'ids' is needed", status.HTTP_400_BAD_REQUEST)
        try:
            _dirname, archive_name = data_uploader.group_export(group_ids, STATIC_CONF['static_path'])
        except Exception as err:
            return Response(str(err), status.HTTP_409_CONFLICT)
        return Response(f'{data_uploader.static_dir_name}/{_dirname}/{archive_name}', status.HTTP_200_OK)
