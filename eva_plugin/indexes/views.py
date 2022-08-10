from rest_framework.response import Response
from rest_framework.exceptions import ParseError, APIException, PermissionDenied

from eva_plugin.indexes.db import db
from eva_plugin.groups.db import db as group_db

from eva_plugin.base_handler import BaseHandler


class IndexesHandler(BaseHandler):
    def get(self, request):
        kwargs = {}

        names_only = self.get_argument('names_only', None)
        if names_only:
            kwargs['names_only'] = names_only

        if 'list_indexes' in self.permissions or 'admin_all' in self.permissions:
            target_user_id = self.get_argument('id', None)
            if target_user_id:
                kwargs['user_id'] = target_user_id
        else:
            kwargs['user_id'] = self.current_user

        indexes = db.get_indexes_data(**kwargs)
        return Response({'data': indexes})


class IndexHandler(BaseHandler):
    def get(self, request):
        index_id = self.get_argument('id', None)
        if not index_id:
            raise ParseError("param 'id' is needed")
        if 'read_indexes' not in self.permissions and 'admin_all' not in self.permissions:
            raise PermissionDenied("no permission for read indexes")

        index_data = db.get_index_data(index_id)
        all_groups = group_db.get_groups_data(names_only=True)
        return Response({'data': index_data, 'groups': all_groups})

    def post(self, request):
        index_name = self.data.get('name', None)
        if not index_name:
            raise ParseError("param 'name' is required")
        if 'create_indexes' not in self.permissions and 'admin_all' not in self.permissions:
            raise PermissionDenied("no permission for create indexes")

        try:
            index_id = db.add_index(name=index_name,
                                    groups=self.data.get('groups', None))
        except Exception as err:
            raise APIException(str(err))
        return Response({'id': index_id})

    def put(self, request):
        index_id = self.data.get('id', None)
        if not index_id:
            raise ParseError("param 'id' is needed")
        if 'manage_indexes' not in self.permissions and 'admin_all' not in self.permissions:
            raise PermissionDenied("no permission for manage indexes")

        db.update_index(index_id=index_id,
                        name=self.data.get('name', None),
                        groups=self.data.get('groups', None))
        return Response({'id': index_id})

    def delete(self, request):
        index_id = self.get_argument('id', None)
        if not index_id:
            raise ParseError("param 'id' is needed")
        if 'delete_indexes' in self.permissions or 'admin_all' in self.permissions:
            index_id = db.delete_index(index_id)
        else:
            raise PermissionDenied("no permission for delete indexes")
        return Response({'id': index_id})
