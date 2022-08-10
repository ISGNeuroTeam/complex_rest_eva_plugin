from rest_framework.response import Response
from rest_framework.exceptions import APIException, PermissionDenied, ParseError, NotFound, NotAuthenticated

from eva_plugin.base_handler import BaseHandler
from eva_plugin.groups.db import db
from eva_plugin.groups.db import db as auth_db
from eva_plugin.indexes.db import db as index_db
from eva_plugin.dashs.db import db as dash_db


class GroupsHandler(BaseHandler):
    def get(self, request):
        kwargs = {}

        if 'list_groups' in self.permissions or 'admin_all' in self.permissions:
            target_user_id = self.get_argument('id', None)
            if target_user_id:
                kwargs['user_id'] = target_user_id
            names_only = self.get_argument('names_only', None)
            if names_only:
                kwargs['names_only'] = names_only
        else:
            kwargs['user_id'] = self.current_user

        groups = db.get_groups_data(**kwargs)
        return Response({'data': groups})


class GroupHandler(BaseHandler):
    def get(self, request):
        group_id = self.get_argument('id', None)
        if not group_id:
            raise ParseError("param 'id' is needed")

        if 'read_groups' not in self.permissions and 'admin_all' not in self.permissions:
            raise PermissionDenied("no permission for read groups")

        try:
            group_data = db.get_group_data(group_id)
        except Exception as err:
            raise ParseError(str(err))

        all_users = auth_db.get_users_data(names_only=True)
        all_indexes = index_db.get_indexes_data(names_only=True)
        all_dashs = dash_db.get_dashs_data(names_only=True)
        return Response({'data': group_data, 'users': all_users,
                    'indexes': all_indexes, 'dashs': all_dashs})

    def post(self, request):
        group_name = self.data.get('name', None)
        color = self.data.get('color', None)
        if None in [group_name, color]:
            raise ParseError("params 'name' and 'color' is required")
        # if 'create_groups' not in self.permissions and 'admin_all' not in self.permissions:
        #     raise tornado.web.HTTPError(403, "no permission for create groups")

        try:
            group_id = db.add_group(name=group_name,
                                         color=color,
                                         users=self.data.get('users', None),
                                         dashs=self.data.get('dashs', None),
                                         indexes=self.data.get('indexes', None))
        except Exception as err:
            raise APIException(str(err))
        return Response({'id': group_id})

    def put(self, request):
        group_id = self.data.get('id', None)
        if not group_id:
            raise ParseError("param 'id' is needed")
        # if 'manage_groups' not in self.permissions and 'admin_all' not in self.permissions:
        #     raise tornado.web.HTTPError(403, "no permission for manage groups")
        db.update_group(group_id=group_id,
                             name=self.data.get('name', None),
                             color=self.data.get('color', None),
                             users=self.data.get('users', None),
                             dashs=self.data.get('dashs', None),
                             indexes=self.data.get('indexes', None))
        return Response({'id': group_id})

    def delete(self, request):
        group_id = self.get_argument('id', None)
        if not group_id:
            raise ParseError("param 'id' is needed")
        if 'delete_groups' in self.permissions or 'admin_all' in self.permissions:
            group_id = db.delete_group(group_id)
        else:
            raise PermissionDenied("no permission for delete groups")
        return Response({'id': group_id})


class GroupDashboardsHandler(BaseHandler):
    def get(self, request):
        group_id = self.get_argument('id', None)
        if not group_id:
            raise ParseError("param 'id' is needed")

        group_dashs = dash_db.get_dashs_data(group_id=group_id)
        return Response({'data': group_dashs})


class UserGroupsHandler(BaseHandler):
    def get(self, request):
        kwargs = {}

        if 'read_groups' not in self.permissions and 'admin_all' not in self.permissions:
            kwargs['user_id'] = self.current_user

        kwargs['names_only'] = self.get_argument('names_only', None)
        user_groups = db.get_groups_data(**kwargs)
        return Response({'data': user_groups})
