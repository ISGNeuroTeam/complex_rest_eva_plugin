from rest.views import APIView
from rest.response import Response, status
from rest.permissions import IsAuthenticated
import uuid
import super_logger
from plugins.db_connector.connector_singleton import db
import json


class DashboardView(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'post', 'put', 'delete']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('dashboards')

    def get(self, request):
        dash_id = request.GET.get('id', None)
        if not dash_id:
            return Response("param 'id' is needed", status.HTTP_400_BAD_REQUEST)
        try:
            dash = db.get_dash_data(dash_id=dash_id)
        except Exception as err:
            return Response(str(err), status.HTTP_409_CONFLICT)
        all_groups = db.get_groups_data(names_only=True)
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
            _id, modified = db.add_dash(name=dash_name,
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
            name, modified = db.update_dash(dash_id=dash_id,
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
        dash_id = db.delete_dash(dash_id=dash_id)
        return Response(
            json.dumps({'id': dash_id}),
            status.HTTP_200_OK
        )
