import json
import uuid

from rest.views import APIView
from rest.response import Response, ErrorResponse, SuccessResponse, status
from rest.permissions import IsAuthenticated
import super_logger

# needed for db connection
from django.conf import settings
from complex_rest.plugins.db_connector.utils.db_connector import PostgresConnector



class ThemeListView(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    logger = super_logger.getLogger('themes')
    db = PostgresConnector(settings.DB_POOL)

    def get(self, request):

        try:
            _offset = request.data['offset']
        except:
            _offset = 0

        try:
            _limit = request.data['limit']
        except:
            _limit = 100

        try:
            themes_list = self.db.get_themes_data(limit=_limit, offset=_offset)
        except Exception as err:
            return Response(
                json.dumps({'status': 'failed', 'error': f'{err}'}, default=str),
                status.HTTP_400_BAD_REQUEST
            )

        self.logger.debug(f'ThemeListView RESPONSE: {themes_list}')
        return \
            SuccessResponse(
                data=themes_list
            )

class ThemeGetView(APIView):
    permission_classes = (IsAuthenticated, )
    http_method_names = ['get']
    logger = super_logger.getLogger('themes')
    db = PostgresConnector(settings.DB_POOL)

    def get(self, request):

        try:
            theme_name = request.data['themeName']
        except:
            theme_name = None

        if theme_name is not None:
            return ErrorResponse(error_message="param 'themeName' is needed")

        self.logger.debug(f'ThemeGetView Request theme name: {theme_name}')

        try:
            theme = self.db.get_theme(theme_name=theme_name)
        except Exception as err:
            return Response(
                json.dumps({'status': 'failed', 'error': f'{err}'}, default=str),
                status.HTTP_400_BAD_REQUEST
            )

        self.logger.debug(f'ThemeGetHandler RESPONSE: {theme}')

        return \
            SuccessResponse(
                json.dumps(theme)
            )

class ThemeCreateView(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']
    logger = super_logger.getLogger('themes')
    db = PostgresConnector(settings.DB_POOL)

    def post(self, request):
        try:
            theme_name = request.data['themeName']
        except:
            theme_name = None

        if theme_name is not None:
            return ErrorResponse(error_message="param 'themeName' is needed")

        # 1. create theme in DB
        try:
            self.logger.debug(f'ThemeHandler create theme, name: {theme_name} with body: {json.dumps(self.data)}')
            theme = self.db.add_theme(theme_name=theme_name,
                                      content=json.dumps(request.data))

        except Exception as err:
            return Response(
                json.dumps({'status': 'failed', 'error': f'{err}'}, default=str),
                status.HTTP_400_BAD_REQUEST
            )

        # 2. return saved theme
        return \
            SuccessResponse(
                json.dumps(theme)
            )


class ThemeDeleteView(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['delete']
    logger = super_logger.getLogger('themes')
    db = PostgresConnector(settings.DB_POOL)

    def delete(self, request):
        try:
            theme_name = request.data['themeName']
        except:
            theme_name = None

        if theme_name is not None:
            return ErrorResponse(error_message="param 'themeName' is needed")

        # 1. check if theme exists
        try:
            theme = self.db.get_theme(theme_name=theme_name)
        except Exception as err:
            return Response(
                json.dumps({'status': 'failed', 'error': f'{err}'}, default=str),
                status.HTTP_400_BAD_REQUEST
            )

        # 2. delete theme
        try:
            deleted_theme_name = self.db.delete_theme(theme_name=theme_name)
            self.logger.debug(f'ThemeHandler Deleted theme name: {deleted_theme_name} with body: {theme}')
        except Exception as err:
            return Response(
                json.dumps({'status': 'failed', 'error': f'{err}'}, default=str),
                status.HTTP_400_BAD_REQUEST
            )

        # 3. return deleted theme
        return \
            SuccessResponse(
                json.dumps(theme)
            )