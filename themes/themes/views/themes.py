import json

from rest.views import APIView
from rest.response import Response, ErrorResponse, SuccessResponse, status
from rest.permissions import IsAuthenticated

db =


class ThemeListView(APIView):
    permission_classes = (IsAuthenticated,)

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
            themes_list = db.get_themes_data(limit=_limit, offset=_offset)
        except Exception as err:
            return ErrorResponse(error_message=str(err))

        self.logger.debug(f'ThemeListView RESPONSE: {themes_list}')
        return \
            SuccessResponse(
                data=themes_list
            )

class ThemeGetView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):

        try:
            theme_name = request.data['themeName']
        except:
            theme_name = None

        if theme_name is not None:
            return ErrorResponse(error_message="param 'themeName' is needed")

        self.logger.debug(f'ThemeGetView Request theme name: {theme_name}')

        try:
            theme = db.get_theme(theme_name=theme_name)
        except Exception as err:
            return ErrorResponse(error_message=str(err))

        self.logger.debug(f'ThemeGetHandler RESPONSE: {theme}')

        return \
            SuccessResponse(
                data=theme
            )

class ThemeView(APIView):
    permission_classes = (IsAuthenticated,)

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
            theme = db.add_theme(theme_name=theme_name,
                                      content=json.dumps(request.data))

        except Exception as err:
            return ErrorResponse(error_message=str(err))

        # 2. return saved theme
        return \
            SuccessResponse(
                data=theme
            )

    def delete(self, request):
        try:
            theme_name = request.data['themeName']
        except:
            theme_name = None

        if theme_name is not None:
            return ErrorResponse(error_message="param 'themeName' is needed")

        # 1. check if theme exists
        try:
            theme = db.get_theme(theme_name=theme_name)
        except Exception as err:
            return ErrorResponse(error_message=str(err))

        # 2. delete theme
        try:
            deleted_theme_name = db.delete_theme(theme_name=theme_name)
            self.logger.debug(f'ThemeHandler Deleted theme name: {deleted_theme_name} with body: {theme}')
        except Exception as err:
            return ErrorResponse(error_message=str(err))

        # 3. return deleted theme
        return \
            SuccessResponse(
                data=theme
            )