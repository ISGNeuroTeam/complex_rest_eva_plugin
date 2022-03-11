# import tarfile
# import tempfile
# from datetime import datetime
# import os
#
# import jwt
#
# from rest.views import APIView
# from rest.response import Response, status
# from rest.permissions import IsAuthenticated
# import uuid
# import super_logger
# from complex_rest.plugins.db_connector.utils.db_connector import PostgresConnector
# from django.conf import settings
# from ..utils.helper_functions import make_unique_name
#
#
# class DashboardImportView(APIView):
#     """
#     View to import dashs, exported with DashExportHandler.
#     Or you can put your own 'eva.dash' file with inner dashs json files.
#     """
#
#     permission_classes = (IsAuthenticated,)
#     http_method_names = ['post']
#     handler_id = str(uuid.uuid4())
#     logger = super_logger.getLogger('dashboards')
#     db = PostgresConnector(settings.DB_POOL)
#
#     def post(self, request):
#         pass
#
