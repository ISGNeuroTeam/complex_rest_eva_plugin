from rest.views import APIView
from rest.response import Response, status
from rest.permissions import IsAdminUser
import uuid
import super_logger
import json
from plugins.db_connector.connector_singleton import db


class DashboardsView(APIView):

    permission_classes = (IsAdminUser,)  # TODO if 'list_dashs' in self.permissions
    http_method_names = ['get']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('dashboards')

    def get(self, request):
        kwargs = {}
        target_group_id = request.GET.get('id', None)
        if target_group_id:
            kwargs['group_id'] = target_group_id
        names_only = request.GET.get('names_only', None)
        if names_only:
            kwargs['names_only'] = names_only
        dashs = db.get_dashs_data(**kwargs)
        return Response(
            json.dumps({'data': dashs}),
            status.HTTP_200_OK
        )
