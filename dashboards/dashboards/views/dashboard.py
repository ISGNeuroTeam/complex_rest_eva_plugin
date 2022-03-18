from rest.views import APIView
from rest.response import Response, status
from rest.permissions import IsAuthenticated
import uuid
import super_logger
from ..utils.ds_wrapper import DataSourceWrapper


class DashboardView(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'post', 'put', 'delete']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('dashboards')
    dswrapper = DataSourceWrapper()

    def get(self, request):
        dash_id = request.GET.get('id', None)
        if not dash_id:
            return Response("param 'id' is needed", status.HTTP_400_BAD_REQUEST)
        try:
            dash = self.dswrapper.get_dashboard(dash_id)
            all_groups = self.dswrapper.get_all_groups(names_only=True)
        except Exception as err:
            return Response(str(err), status.HTTP_409_CONFLICT)
        return Response(
            {'data': dash, 'groups': all_groups},
            status.HTTP_200_OK
        )

    def post(self, request):
        dash_name = request.data.get('name', None)
        dash_body = request.data.get('body', "")
        dash_groups = request.data.get('groups', None)
        if not dash_name:
            return Response("params 'name' is needed", status.HTTP_400_BAD_REQUEST)
        try:
            _id, modified = self.dswrapper.add_dashboard(dash_name, dash_body, dash_groups)
        except Exception as err:
            return Response(str(err), status.HTTP_409_CONFLICT)
        return Response(
            {'id': _id, 'modified': modified},
            status.HTTP_200_OK
        )

    def put(self, request):
        dash_id = request.data.get('id', None)
        if not dash_id:
            return Response("param 'id' is needed", status.HTTP_400_BAD_REQUEST)
        try:
            name, modified = self.dswrapper.update_dashboard(dash_id=dash_id,
                                            name=request.data.get('name', None),
                                            body=request.data.get('body', None),
                                            groups=request.data.get('groups', None))
        except Exception as err:
            return Response(str(err), status.HTTP_409_CONFLICT)
        return Response(
            {'id': dash_id, 'name': name, 'modified': modified},
            status.HTTP_200_OK
        )

    def delete(self, request):
        dash_id = request.data.get('id', None)
        if not dash_id:
            return Response("param 'id' is needed", status.HTTP_400_BAD_REQUEST)
        dash_id = self.dswrapper.delete_dashboard(dash_id)
        return Response(
            {'id': dash_id},
            status.HTTP_200_OK
        )
