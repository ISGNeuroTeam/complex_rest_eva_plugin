from rest.views import APIView
from rest.response import Response, status
from rest.permissions import IsAuthenticated
import uuid
import super_logger
from ..utils.ds_wrapper import dswrapper


class DashByNameView(APIView):

    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('dashboards')

    def get(self, request):
        dash_name = request.GET.get('name', None)
        dash_idgroup = request.GET.get('idgroup', None)
        if not dash_name:
            return Response("param 'name' is needed", status.HTTP_400_BAD_REQUEST)
        if not dash_idgroup:
            return Response("param 'idgroup' is needed", status.HTTP_400_BAD_REQUEST)
        try:
            dash = dswrapper.get_dashboard_by_name(dash_name, dash_idgroup)
        except Exception as err:
            return Response(str(err), status.HTTP_409_CONFLICT)
        return Response({'data': dash}, status.HTTP_200_OK)
