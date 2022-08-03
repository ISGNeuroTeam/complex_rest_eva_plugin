import json
import uuid

from rest.views import APIView
from rest.response import Response, ErrorResponse, SuccessResponse, status
from rest.permissions import IsAuthenticated, AllowAny
import logging

from plugins.themes.utils.theme_manager import ThemeManager


class ThemeListView(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    logger = logging.getLogger('themes')

    def get(self, request):

        _offset = request.query_params.get('offset', 0)
        _limit = request.query_params.get('limit', 100)

        try:
            themes_list = ThemeManager.get_themes(limit=_limit, offset=_offset)
        except Exception as err:
            return Response(
                {'status': 'failed', 'error': str(err)},
                status.HTTP_409_CONFLICT
            )

        self.logger.debug(f'ThemeListView RESPONSE: {themes_list}')
        return \
            Response(
                themes_list,
                status.HTTP_200_OK
            )

class ThemeGetView(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    logger = logging.getLogger('themes')

    def get(self, request):

        theme_name = request.query_params.get('themeName', None)

        if theme_name is None:
            return ErrorResponse(error_message="param 'themeName' is needed")

        self.logger.debug(f'ThemeGetView Request theme name: {theme_name}')

        try:
            theme = ThemeManager.get_theme(theme_name=theme_name)
        except Exception as err:
            return Response(
                {'status': 'failed', 'error': str(err)},
                status.HTTP_409_CONFLICT
            )

        self.logger.debug(f'ThemeGetHandler RESPONSE: {theme}')

        return Response(
                theme,
                status.HTTP_200_OK
            )

class ThemeCreateView(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']
    logger = logging.getLogger('themes')

    def post(self, request):
        theme_name = request.data.get('themeName', None)

        if theme_name is None:
            return ErrorResponse(error_message="param 'themeName' is needed")

        try:
            self.logger.debug(f'ThemeHandler create theme, name: {theme_name} with body: {json.dumps(request.data)}')
            theme = ThemeManager.create_theme(theme_name=theme_name, content=json.dumps(request.data))

        except Exception as err:
            return Response(
                {'status': 'failed', 'error': str(err)},
                status.HTTP_409_CONFLICT
            )

        return Response(
                theme,
                status.HTTP_200_OK
            )


class ThemeDeleteView(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['delete']
    logger = logging.getLogger('themes')

    def delete(self, request):
        theme_name = request.data.get('themeName', None)

        if theme_name is None:
            return ErrorResponse(error_message="param 'themeName' is needed")

        try:
            theme = ThemeManager.delete_theme(theme_name=theme_name)
            self.logger.debug(f'ThemeHandler Deleted theme name: {theme_name} with body: {theme}')
        except Exception as err:
            return Response(
                {'status': 'failed', 'error': str(err)},
                status.HTTP_409_CONFLICT
            )

        # 3. return deleted theme
        return Response(
                theme,
                status.HTTP_200_OK
            )
