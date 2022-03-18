import json
from rest.views import APIView
from rest.response import Response, status
from rest.permissions import IsAuthenticated
import uuid
import super_logger
from ..utils.ds_wrapper import DataSourceWrapper

class GroupDashboardsView(APIView):

    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('dashboards')
    dswrapper = DataSourceWrapper()

    def get(self, request):
        group_id = request.get('id', None)
        if not group_id:
            return Response("param 'id' is needed", status.HTTP_400_BAD_REQUEST)
        group_dashes = self.dswrapper.get_dashboards(group_id=group_id)
        Response(json.dumps({'data': group_dashes}), status.HTTP_200_OK)
