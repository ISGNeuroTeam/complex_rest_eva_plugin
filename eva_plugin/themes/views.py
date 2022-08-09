import json
import logging

from rest_framework.response import Response
from rest_framework.exceptions import APIException, ParseError
from eva_plugin.base_handler import BaseHandler
from eva_plugin.themes.db import db

logger = logging.getLogger('eva_plugin.themes')


class ThemeListHandler(BaseHandler):
    def initial(self, request, *args, **kwargs):
        super(BaseHandler, self).initial(request, *args, **kwargs)
        self._set_request_params(request)

    def get(self, request):
        _offset = self.get_argument('offset', 0)
        _limit = self.get_argument('limit', 100)
        try:
            themes_list = db.get_themes_data(limit=_limit, offset=_offset)
        except Exception as err:
            raise APIException(str(err))
        logger.debug(f'ThemeListHandler RESPONSE: {themes_list}')
        return Response(themes_list)


class ThemeGetHandler(BaseHandler):
    def initial(self, request, *args, **kwargs):
        super(BaseHandler, self).initial(request, *args, **kwargs)
        self._set_request_params(request)

    def get(self, request):
        theme_name = self.get_argument('themeName', None)
        if not theme_name:
            raise ParseError("param 'themeName' is needed")
        logger.debug(f'ThemeGetHandler Request theme name: {theme_name}')
        try:
            # theme = db.get_dash_data(dash_id=dash_id)
            theme = db.get_theme(theme_name=theme_name)
        except Exception as err:
            raise APIException(str(err))
        logger.debug(f'ThemeGetHandler RESPONSE: {theme}')
        return Response(theme)


class ThemeHandler(BaseHandler):

    def post(self, request):
        theme_name = self.data.get('themeName', None)
        if not theme_name:
            raise ParseError("param 'themeName' is needed for creating theme")

        # 1. create theme in DB
        try:
            logger.debug(f'ThemeHandler create theme, name: {theme_name} with body: {json.dumps(self.data)}')
            theme = db.add_theme(theme_name=theme_name,
                                      content=json.dumps(self.data))
        except Exception as err:
            raise APIException(str(err))

        # 2. return saved theme
        return Response(theme)

    def delete(self, request):
        theme_name = self.data.get('themeName', None)
        try:
            # theme = db.get_dash_data(dash_id=dash_id)
            theme = db.get_theme(theme_name=theme_name)
        except Exception as err:
            raise APIException(str(err))

        #2. delete theme
        try:
            deleted_theme_name = db.delete_theme(theme_name=theme_name)
            logger.debug(f'ThemeHandler Deleted theme name: {deleted_theme_name} with body: {theme}')
        except Exception as err:
            raise APIException(str(err))

        #3. return deleted theme
        return Response(theme)

