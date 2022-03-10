from rest.views import APIView
from rest.response import Response, status
from rest.permissions import IsAuthenticated
import uuid
import super_logger
from complex_rest.plugins.db_connector.utils.db_connector import PostgresConnector
from django.conf import settings
import json


class DashboardsView(APIView):

    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('dashboards')
    db = PostgresConnector(settings.DB_POOL)

    def get(self, request):
        kwargs = {}
        target_group_id = request.GET.get('id', None)
        if target_group_id:
            kwargs['group_id'] = target_group_id
        names_only = request.GET.get('names_only', None)
        if names_only:
            kwargs['names_only'] = names_only
        dashs = self.db.get_dashs_data(**kwargs)
        return Response(
            {'data': dashs},
            status.HTTP_200_OK
        )
