from eva_plugin.base_handler import BaseHandler
from eva_plugin.catalogs.db import db
from rest_framework.response import Response
from rest_framework.exceptions import ParseError, APIException


class CatalogsListHandler(BaseHandler):
    def get(self):
        _offset = self.get_argument('offset', 0)
        _limit = self.get_argument('limit', 10)

        catalogs = db.get_catalogs_data(limit=_limit, offset=_offset)
        return Response({'data': catalogs, 'count': db.get_catalogs_count()})


class CatalogHandler(BaseHandler):
    def get(self, request):
        catalog_id = self.get_argument('id', None)
        if not catalog_id:
            raise ParseError("param 'id' is needed")
        try:
            catalog = db.get_catalog(catalog_id=catalog_id)
        except Exception as err:
            raise ParseError(str(err))
        return Response({'data': catalog})

    def post(self, request):
        catalog_name = self.data.get('name', None)
        content = self.data.get('content', None)
        if None in [catalog_name, content]:
            raise ParseError("params 'name' and 'content' is needed")
        try:
            catalog_id = db.add_catalog(name=catalog_name,
                                             content=content)
        except Exception as err:
            raise APIException(str(err))
        return Response({'id': catalog_id})

    def put(self, request):
        catalog_id = self.data.get('id', None)
        catalog_name = self.data.get('name', None)
        content = self.data.get('content', None)
        if not catalog_id:
            raise ParseError("param 'id' is needed")
        try:
            catalog_id = db.update_catalog(catalog_id=catalog_id,
                                                name=catalog_name,
                                                content=content)
        except Exception as err:
            raise APIException(str(err))
        return Response({'id': catalog_id})

    def delete(self, request):
        catalog_id = self.get_argument('id', None)
        if not catalog_id:
            raise ParseError("params 'id' is needed")
        catalog_id = db.delete_catalog(catalog_id=catalog_id)
        return Response({'id': catalog_id})

