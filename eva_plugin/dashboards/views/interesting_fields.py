from rest.views import APIView
from rest.response import Response, status
from rest.permissions import IsAuthenticated
from ..utils.interesting_fields_builder import InterestingFieldsBuilder
from ..utils.interesting_fields_loader import InterestingFieldsLoader
import uuid
import logging
from eva_plugin.settings import STATIC_CONF, MEM_CONF


class InterestingFieldsView(APIView):
    """
    Returns a list of dictionaries where every dictionary represents interesting fields for one column of data

    interesting fields consist of:
    :id: serial number of a column
    :text: name of a column
    :totalCount: number of not empty cells in the column (null is considered an empty cell)
    :static: list of dictionaries where every dictionary is an info about every unique value in a column consists of:
            :value: value itself
            :count: how many times the value appears in the column
            :%: percent of count from all rows in the data table
    """

    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    handler_id = str(uuid.uuid4())
    logger = logging.getLogger('dashboards')

    def __init__(self):
        super().__init__()
        self.builder = InterestingFieldsBuilder()
        self.loader = InterestingFieldsLoader(MEM_CONF, STATIC_CONF)

    def get(self, request):
        cid = dict(request.GET).get('cid')
        if not cid:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        cid = cid[0]
        try:
            data = self.loader.load_data(cid)
            interesting_fields = self.builder.get_interesting_fields(data)
        except Exception as e:
            return Response(
                {'status': 'failed', 'error': f'{e} cid {cid}'},
                status.HTTP_400_BAD_REQUEST
            )
        return Response(
            interesting_fields,
            status.HTTP_200_OK
        )
