from rest.views import APIView
from rest.response import Response, status
from rest.permissions import IsAuthenticated
import uuid
import super_logger
import json
from plugins.db_connector.connector_singleton import db


class DashByNameView(APIView):

    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('dashboards')

    def get(self, request):
        dash_name = request.data.get('name', None)
        dash_idgroup = request.data.get('idgroup', None)
        if not dash_name:
            return Response("param 'name' is needed", status.HTTP_400_BAD_REQUEST)
        if not dash_idgroup:
            return Response("param 'idgroup' is needed", status.HTTP_400_BAD_REQUEST)
        try:
            dash_name = dash_name.replace('"', '')
            # FIXME need remove double quote replacement
            dash = db.get_dash_data_by_name(dash_name=dash_name, dash_group=dash_idgroup)
        except Exception as err:
            return Response(str(err), status.HTTP_409_CONFLICT)
        return Response(json.dumps({'data': dash}), status.HTTP_200_OK)
