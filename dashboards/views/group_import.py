from rest.views import APIView
from rest.response import Response, status
from rest.permissions import IsAuthenticated
import uuid
import super_logger
from ..utils.data_uploader import data_uploader


class GroupImportView(APIView):
    """
    View to import groups, exported with GroupExportHandler.
    Or you can put your own 'eva.group' file with dirs named group_id
    with inner dashes json files.
    """

    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('dashboards')

    def post(self, request):
        files = request.FILES
        if not files or not files.get('body'):
            return Response({'error': 'no file in payload'}, status.HTTP_204_NO_CONTENT)
        try:
            data_uploader.group_import(files)
        except Exception as err:
            return Response({'error': str(err)}, status.HTTP_400_BAD_REQUEST)
        return Response({'status': 'success'})
