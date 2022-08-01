from rest.views import APIView
from rest.response import Response, status
from rest.permissions import IsAuthenticated
import uuid
import logging
from ..utils.data_uploader import data_uploader
from ..settings import STATIC_CONF


class DashboardExportView(APIView):
    """
    View to export one or more dash object in '.json' format files.
    Json files returns in 'eva.dash' package with datetime-name.
    """

    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    handler_id = str(uuid.uuid4())
    logger = logging.getLogger('dashboards')
    static_conf = STATIC_CONF

    def get(self, request):
        dash_ids = request.GET.get('ids', None)
        if not dash_ids:
            return Response("param 'ids' is needed", status.HTTP_400_BAD_REQUEST)
        try:
            _dirname, archive_name = data_uploader.dash_export(dash_ids, STATIC_CONF)
        except Exception as e:
            return Response(str(e), status.HTTP_409_CONFLICT)
        return Response(
            f'{data_uploader.static_dir_name}/{_dirname}/{archive_name}',
            status.HTTP_200_OK
        )
