import json
import uuid

from rest.views import APIView
from rest.response import Response, ErrorResponse, SuccessResponse, status
from rest.permissions import IsAuthenticated, AllowAny
import super_logger

# needed for db connection
from plugins.db_connector.connector_singleton import db



class ThemeListView(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    logger = super_logger.getLogger('themes')

    def get(self, request):

        _offset = request.query_params.get('offset', 0)
        _limit = request.query_params.get('limit', 100)

        try:
            themes_list = db.get_themes_data(limit=_limit, offset=_offset)
        except Exception as err:
            return Response(
                {'status': 'failed', 'error': str(err)},
                status.HTTP_409_CONFLICT
            )

        self.logger.debug(f'ThemeListView RESPONSE: {themes_list}')
        return \
            SuccessResponse(
                data={"data":themes_list}
            )

class ThemeGetView(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    logger = super_logger.getLogger('themes')

    def get(self, request):

        theme_name = request.query_params.get('themeName', None)

        if theme_name is None:
            return ErrorResponse(error_message="param 'themeName' is needed")

        self.logger.debug(f'ThemeGetView Request theme name: {theme_name}')

        try:
            theme = db.get_theme(theme_name=theme_name)
        except Exception as err:
            return Response(
                {'status': 'failed', 'error': str(err)},
                status.HTTP_409_CONFLICT
            )

        self.logger.debug(f'ThemeGetHandler RESPONSE: {theme}')

        return \
            SuccessResponse(
                data=theme
            )

class ThemeCreateView(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']
    logger = super_logger.getLogger('themes')

    def post(self, request):
        theme_name = request.data.get('themeName', None)

        if theme_name is None:
            return ErrorResponse(error_message="param 'themeName' is needed")

        # 1. create theme in DB
        try:
            self.logger.debug(f'ThemeHandler create theme, name: {theme_name} with body: {json.dumps(request.data)}')
            theme = db.add_theme(theme_name=theme_name,
                                      content=json.dumps(request.data))

        except Exception as err:
            return Response(
                {'status': 'failed', 'error': str(err)},
                status.HTTP_409_CONFLICT
            )

        # 2. return saved theme
        return \
            SuccessResponse(
                data=theme
            )


class ThemeDeleteView(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['delete']
    logger = super_logger.getLogger('themes')

    def delete(self, request):
        theme_name = request.data.get('themeName', None)

        if theme_name is None:
            return ErrorResponse(error_message="param 'themeName' is needed")

        # 1. check if theme exists
        try:
            theme = db.get_theme(theme_name=theme_name)
        except Exception as err:
            return Response(
                {'status': 'failed', 'error': str(err)},
                status.HTTP_409_CONFLICT
            )

        # 2. delete theme
        try:
            deleted_theme_name = db.delete_theme(theme_name=theme_name)
            self.logger.debug(f'ThemeHandler Deleted theme name: {deleted_theme_name} with body: {theme}')
        except Exception as err:
            return Response(
                {'status': 'failed', 'error': str(err)},
                status.HTTP_409_CONFLICT
            )

        # 3. return deleted theme
        return \
            SuccessResponse(
                data=theme
            )
