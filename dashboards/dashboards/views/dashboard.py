from rest.views import APIView
from rest.response import Response, status
from rest.permissions import IsAuthenticated
import uuid
import super_logger
from complex_rest.plugins.db_connector.utils.db_connector import PostgresConnector
from django.conf import settings
import json


class DashboardView(APIView):

    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'post', 'put', 'delete']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('dashboards')
    db = PostgresConnector(settings.DB_POOL)

    def get(self, request):
        dash_id = request.GET.get('id', None)
        if not dash_id:
            return Response("param 'id' is needed", status.HTTP_400_BAD_REQUEST)
        try:
            dash = self.db.get_dash_data(dash_id=dash_id)
        except Exception as err:
            return Response(str(err), status.HTTP_409_CONFLICT)
        all_groups = self.db.get_groups_data(names_only=True)
        return Response(
            json.dumps({'data': dash, 'groups': all_groups}),
            status.HTTP_200_OK
        )

    def post(self, request):
        dash_name = request.data.get('name', None)
        dash_body = request.data.get('body', "")
        dash_groups = request.data.get('groups', None)
        if not dash_name:
            return Response("params 'name' is needed", status.HTTP_400_BAD_REQUEST)
        try:
            _id, modified = self.db.add_dash(name=dash_name,
                                             body=dash_body,
                                             groups=dash_groups)
        except Exception as err:
            return Response(str(err), status.HTTP_409_CONFLICT)
        return Response(
            json.dumps({'id': _id, 'modified': modified}),
            status.HTTP_200_OK
        )

    def put(self, request):
        dash_id = request.data.get('id', None)
        if not dash_id:
            return Response("param 'id' is needed", status.HTTP_400_BAD_REQUEST)
        try:
            name, modified = self.db.update_dash(dash_id=dash_id,
                                                 name=request.data.get('name', None),
                                                 body=request.data.get('body', None),
                                                 groups=request.data.get('groups', None))
        except Exception as err:
            return Response(str(err), status.HTTP_409_CONFLICT)
        return Response(
            json.dumps({'id': dash_id, 'name': name, 'modified': modified}),
            status.HTTP_200_OK
        )

    def delete(self, request):
        dash_id = request.get_argument('id', None)
        if not dash_id:
            return Response("param 'id' is needed", status.HTTP_400_BAD_REQUEST)
        dash_id = self.db.delete_dash(dash_id=dash_id)
        return Response(
            json.dumps({'id': dash_id}),
            status.HTTP_200_OK
        )
