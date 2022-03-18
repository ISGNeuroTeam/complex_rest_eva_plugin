from rest.views import APIView
from rest.response import Response, status
from rest.permissions import IsAdminUser
from ..utils.ds_wrapper import dswrapper
import uuid
import super_logger


class DashboardsView(APIView):

    permission_classes = (IsAdminUser,)  # TODO if 'list_dashs' in self.permissions
    http_method_names = ['get']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('dashboards')

    def get(self, request):
        target_group_id = request.GET.get('id', None)
        names_only = request.GET.get('names_only', None)
        dashes = dswrapper.get_dashboards(target_group_id, names_only)
        return Response(
            {'data': dashes},
            status.HTTP_200_OK
        )
