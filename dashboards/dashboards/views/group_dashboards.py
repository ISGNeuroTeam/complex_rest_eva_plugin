import json
from plugins.db_connector.connector_singleton import db
from rest.views import APIView
from rest.response import Response, status
from rest.permissions import IsAuthenticated
import uuid
import super_logger


class GroupDashboardsView(APIView):

    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('dashboards')

    def get(self, request):
        group_id = request.get('id', None)
        if not group_id:
            return Response("param 'id' is needed", 400)
        group_dashs = db.get_dashs_data(group_id=group_id)
        Response(json.dumps({'data': group_dashs}), status.HTTP_200_OK)
