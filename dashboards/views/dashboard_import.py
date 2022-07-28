from rest.views import APIView
from rest.response import Response, status
from rest.permissions import IsAuthenticated
import uuid
import super_logger
from ..utils.data_uploader import data_uploader


class DashboardImportView(APIView):
    """
    View to import dashs, exported with DashExportHandler.
    Or you can put your own 'eva.dash' file with inner dashs json files.
    """

    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('dashboards')

    def post(self, request):
        group = [request.data.get('group').encode()]
        files = request.FILES

        if not files or not files.get('body'):
            return Response({'error': 'no file in payload'},
                            status.HTTP_204_NO_CONTENT)
        try:
            data_uploader.dash_import(files, group)
        except Exception as err:
            return Response(str(err), status.HTTP_400_BAD_REQUEST)
        return Response({'status': 'success'}, status.HTTP_200_OK)
