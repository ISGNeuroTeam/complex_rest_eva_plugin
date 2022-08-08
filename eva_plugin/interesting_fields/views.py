import json
from typing import Dict

from rest_framework.response import Response
from rest_framework.views import APIView

from eva_plugin.base_handler import BaseHandler
from eva_plugin.tools.interesting_fields_builder import InterestingFieldsBuilder
from eva_plugin.tools.interesting_fields_loader import InterestingFieldsLoader, BaseLoaderError
from eva_plugin.settings import MEM_CONF, STATIC_CONF


class GetInterestingFields(APIView):
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

    def __init__(self):
        super(GetInterestingFields, self).__init__()

        self.builder = InterestingFieldsBuilder()
        self.loader = InterestingFieldsLoader(MEM_CONF, STATIC_CONF)

    def get(self, request):
        params = self.request.query_arguments
        cid = params.get('cid')[0].decode()
        from_time = params.get('from')
        to_time = params.get('to')
        if from_time:
            from_time = from_time[0].decode()
            if not from_time.isdigit():
                return Response({'status': 'failed', 'error': f'from: {from_time} not a number'},
                                             default=str)
            from_time = int(from_time)
        if to_time:
            to_time = to_time[0].decode()
            if not to_time.isdigit():
                return Response(json.dumps({'status': 'failed', 'error': f'to: {to_time} not a number'},
                                             default=str))
            to_time = int(to_time)
        try:
            data = self.loader.load_data(cid, from_time, to_time)
            interesting_fields = self.builder.get_interesting_fields(data)
        except BaseLoaderError as e:
            return Response(json.dumps({'status': 'failed', 'error': e}, default=str))
        except Exception as e:
            return Response(json.dumps({'status': 'failed', 'error': f'{e} cid {cid}'}, default=str))
        return Response(json.dumps(interesting_fields))
