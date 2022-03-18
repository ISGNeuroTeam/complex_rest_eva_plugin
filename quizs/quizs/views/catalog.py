from rest.permissions import IsAuthenticated
from rest.response import Response, status
from rest.views import APIView
import super_logger
import uuid
import json

from ..settings import DB_CONN


class CatalogsListHandlerView(APIView):

    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('quizs')

    def get(self, request):

        offset, limit = request.GET.get('offset', 0), request.GET.get('limit', 10)

        catalogs = DB_CONN.get_catalogs_data(limit=limit, offset=offset)

        content = {'data': catalogs, 'count': DB_CONN.get_catalogs_count()}
        return Response(content, status.HTTP_200_OK)


class CatalogHandlerView(APIView):

    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'post', 'put', 'delete']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('quizs')

    def get(self, request):

        catalog_id = request.GET.get('id', None)

        if not catalog_id:
            return Response(
                        json.dumps({'status': 'failed', 'error': "param 'id' is needed"},
                                   default=str),
                        status.HTTP_400_BAD_REQUEST
                    )

        try:
            catalog = DB_CONN.get_catalog(catalog_id=catalog_id)
        except Exception as err:
            return Response(
                json.dumps({'status': 'failed', 'error': str(err)},
                           default=str),
                status.HTTP_400_BAD_REQUEST
            )

        content = {'data': catalog}
        return Response(content, status.HTTP_200_OK)

    def post(self, request):

        data = request.data

        catalog_name = data.get('name', None)
        content = data.get('content', None)

        if None in [catalog_name, content]:
            return Response(
                json.dumps({'status': 'failed', 'error': "params 'name' and 'content' is needed"},
                           default=str),
                status.HTTP_400_BAD_REQUEST
            )

        try:
            catalog_id = DB_CONN.add_catalog(name=catalog_name,
                                             content=content)
        except Exception as err:
            return Response(
                json.dumps({'status': 'failed', 'error': str(err)},
                           default=str),
                status.HTTP_409_CONFLICT
            )

        content = {'id': catalog_id}
        return Response(content, status.HTTP_200_OK)

    def put(self, request):

        data = request.data

        catalog_id = data.get('id', None)
        catalog_name = data.get('name', None)
        content = data.get('content', None)

        if not catalog_id:
            return Response(
                json.dumps({'status': 'failed', 'error': "param 'id' is needed"},
                           default=str),
                status.HTTP_400_BAD_REQUEST
            )

        try:
            catalog_id = DB_CONN.update_catalog(catalog_id=catalog_id,
                                                name=catalog_name,
                                                content=content)
        except Exception as err:
            return Response(
                json.dumps({'status': 'failed', 'error': str(err)},
                           default=str),
                status.HTTP_409_CONFLICT
            )

        content = {'id': catalog_id}
        return Response(content, status.HTTP_200_OK)

    def delete(self, request):

        catalog_id = request.GET.get('id', None)

        if not catalog_id:
            return Response(
                json.dumps({'status': 'failed', 'error': "param 'id' is needed"},
                           default=str),
                status.HTTP_400_BAD_REQUEST
            )
        catalog_id = DB_CONN.delete_catalog(catalog_id=catalog_id)

        content = {'id': catalog_id}
        return Response(content, status.HTTP_200_OK)
