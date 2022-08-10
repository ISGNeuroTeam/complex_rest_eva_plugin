import bcrypt

from rest_framework.response import Response
from rest_framework.exceptions import ParseError, APIException, PermissionDenied

from eva_plugin.auth.db import db
from eva_plugin.groups.db import db as group_db

from eva_plugin.base_handler import BaseHandler


class UsersHandler(BaseHandler):
    def get(self, request):
        kwargs = {}

        names_only = self.get_argument('names_only', None)
        if names_only:
            kwargs['names_only'] = names_only

        if 'list_users' not in self.permissions and 'admin_all' not in self.permissions:
            kwargs['user_id'] = self.current_user

        users = db.get_users_data(**kwargs)
        return Response({'data': users})


class UserHandler(BaseHandler):
    def get(self, request):
        target_user_id = self.get_argument('id', None)
        if not target_user_id:
            raise ParseError("param 'id' is needed")
        if 'read_users' in self.permissions or 'admin_all' in self.permissions:
            user_data = db.get_user_data(user_id=target_user_id)
            all_roles = db.get_roles_data(names_only=True)
            all_groups = group_db.get_groups_data(names_only=True)
            user_data = {'data': user_data, 'roles': all_roles, 'groups': all_groups}
        elif int(target_user_id) == self.current_user:
            user_data = db.get_user_data(user_id=target_user_id)
            user_data = {'data': user_data}
        else:
            raise PermissionDenied("no permission for read users")
        return Response(user_data)

    def post(self, request):
        if 'create_users' in self.permissions or 'admin_all' in self.permissions:
            password = self.data.get("password", None)
            username = self.data.get("name", None)
            if None in [password, username]:
                raise ParseError("params 'name' and 'password' is required")

            hashed_password = bcrypt.hashpw(
                password.encode('utf-8'),
                bcrypt.gensalt(),
            )
            try:
                user_id = db.add_user(name=username,
                                           password=hashed_password.decode('utf-8'),
                                           roles=self.data.get('roles', None),
                                           groups=self.data.get('groups', None))
                return Response({'id': user_id})
            except Exception as err:
                raise APIException(str(err))
        else:
            raise PermissionDenied("no permission for create roles")

    def put(self, request):
        target_user_id = self.data.get('id', None)
        if not target_user_id:
            raise ParseError("param 'id' is needed")

        if 'manage_users' in self.permissions or 'admin_all' in self.permissions:
            new_password = self.data.get("password", None)
            if new_password:
                new_hashed_password = bcrypt.hashpw(
                    new_password.encode('utf-8'),
                    bcrypt.gensalt(),
                )
                new_password = new_hashed_password.decode('utf-8')
        else:
            user_data = db.get_auth_data(user_id=target_user_id)
            stored_password = user_data.pop("password")

            old_password = self.data.get("old_password", None)
            new_password = self.data.get("new_password", None)

            if new_password and old_password:
                password_equal = bcrypt.checkpw(
                    old_password.encode('utf-8'),
                    stored_password.encode('utf-8'),
                )

                if not password_equal:
                    raise PermissionDenied("old password value is incorrect")

                new_hashed_password = bcrypt.hashpw(
                    new_password.encode('utf-8'),
                    bcrypt.gensalt(),
                )
                new_password = new_hashed_password.decode('utf-8')

        new_username = self.data.get('name', None)
        user_id = db.update_user(user_id=target_user_id,
                                      name=new_username,
                                      password=new_password,
                                      roles=self.data.get('roles', None),
                                      groups=self.data.get('groups', None))

        return Response({'id': user_id})

    def delete(self, request):
        target_user_id = self.get_argument('id', None)
        if not target_user_id:
            raise ParseError("param 'id' is needed")

        if 'delete_users' in self.permissions or 'admin_all' in self.permissions:
            user_id = db.delete_user(target_user_id)
        else:
            raise PermissionDenied("no permission for delete roles")
        return Response({'id': user_id})


class RolesHandler(BaseHandler):
    def get(self, request):
        kwargs = {}

        if 'list_roles' in self.permissions or 'admin_all' in self.permissions:
            target_user_id = self.get_argument('id', None)
            if target_user_id:
                kwargs['user_id'] = target_user_id
            names_only = self.get_argument('names_only', None)
            if names_only:
                kwargs['names_only'] = names_only
        else:
            kwargs['user_id'] = self.current_user

        roles = db.get_roles_data(**kwargs)
        return Response({'data': roles})


class RoleHandler(BaseHandler):
    def get(self, request):
        role_id = self.get_argument('id', None)
        if not role_id:
            raise ParseError("param 'id' is needed")
        if 'read_roles' in self.permissions or 'admin_all' in self.permissions:
            role_data = db.get_role_data(role_id)
            all_users = db.get_users_data(names_only=True)
            all_permissions = db.get_permissions_data(names_only=True)
        else:
            raise PermissionDenied("no permission for read roles")
        return Response({'data': role_data, 'users': all_users, 'permissions': all_permissions})

    def post(self, request):
        role_name = self.data.get('name', None)
        if not role_name:
            raise ParseError("param 'name' is required")
        if 'create_roles' not in self.permissions and 'admin_all' not in self.permissions:
            raise PermissionDenied("no permission for create roles")

        try:
            role_id = db.add_role(name=role_name,
                                       users=self.data.get('users', None),
                                       permissions=self.data.get('permissions', None))
        except Exception as err:
            raise APIException(str(err))
        return Response({'id': role_id})

    def put(self, request):
        role_id = self.data.get('id', None)
        if not role_id:
            raise ParseError("param 'id' is needed")
        if 'manage_roles' not in self.permissions and 'admin_all' not in self.permissions:
            raise PermissionDenied("no permission for manage roles")

        db.update_role(role_id=role_id,
                            name=self.data.get('name', None),
                            users=self.data.get('users', None),
                            permissions=self.data.get('permissions', None))

        return Response({'id': role_id})

    def delete(self, request):
        role_id = self.get_argument('id', None)
        if not role_id:
            raise ParseError("param 'id' is needed")

        if 'delete_roles' in self.permissions or 'admin_all' in self.permissions:
            role_id = db.delete_role(role_id)
        else:
            raise PermissionDenied("no permission for delete roles")
        return Response({'id': role_id})


class PermissionsHandler(BaseHandler):
    def get(self, request):
        kwargs = {}

        if 'list_permissions' in self.permissions or 'admin_all' in self.permissions:
            target_user_id = self.get_argument('id', None)
            if target_user_id:
                kwargs['user_id'] = target_user_id
            names_only = self.get_argument('names_only', None)
            if names_only:
                kwargs['names_only'] = names_only
        else:
            kwargs['user_id'] = self.current_user

        permissions = db.get_permissions_data(**kwargs)
        return Response({'data': permissions})


class PermissionHandler(BaseHandler):
    def get(self, request):
        permission_id = self.get_argument('id', None)
        if not permission_id:
            raise ParseError("param 'id' is needed")
        if 'read_permission' not in self.permissions and 'admin_all' not in self.permissions:
            raise PermissionDenied("no permission for read permissions")

        permission_data = db.get_permission_data(permission_id)
        all_roles = db.get_roles_data(names_only=True)
        return Response({'data': permission_data, 'roles': all_roles})

    def post(self, request):
        permission_name = self.data.get('name', None)
        if not permission_name:
            raise ParseError("param 'name' is required")
        if 'create_permissions' not in self.permissions and 'admin_all' not in self.permissions:
            raise PermissionDenied("no permission for create permissions")

        try:
            permission_id = db.add_permission(name=permission_name,
                                                   roles=self.data.get('roles', None))
        except Exception as err:
            raise APIException(str(err))
        return Response({'id': permission_id})

    def put(self, request):
        permission_id = self.data.get('id', None)
        if not permission_id:
            raise ParseError("param 'id' is needed")
        if 'manage_permissions' not in self.permissions and 'admin_all' not in self.permissions:
            raise PermissionDenied("no permission for manage permissions")

        db.update_permission(permission_id=permission_id,
                                  name=self.data.get('name', None),
                                  roles=self.data.get('roles', None))
        return Response({'id': permission_id})

    def delete(self, request):
        permission_id = self.get_argument('id', None)
        if not permission_id:
            raise ParseError("param 'id' is needed")
        if 'delete_permissions' in self.permissions or 'admin_all' in self.permissions:
            permission_id = db.delete_permission(permission_id)
        else:
            raise PermissionDenied("no permission for delete permissions")
        return Response({'id': permission_id})


class UserPermissionsHandler(BaseHandler):
    def get(self, request):
        return Response({'data': self.permissions})


class UserSettingHandler(BaseHandler):
    def get(self, request):
        self.logger.debug("User = '%s'" % self.current_user,
                          extra={'hid': self.handler_id})
        user_setting = db.get_user_setting(self.current_user)
        self.logger.debug("Returned user setting jjjj= '%s'" % user_setting)
        return Response(user_setting)

    def put(self, request):
        new_setting = self.data.get("setting", None)
        if not new_setting:
            raise ParseError("param 'setting' is needed")

        self.logger.debug("User = '%s', with setting = '%s'" % (self.current_user, new_setting),
                          extra={'hid': self.handler_id})
        try:
            status = db.update_user_setting(self.current_user, new_setting)
            if status:
                return Response('{"status": "success"}')
            else:
                raise APIException(str("Update error"))
        except Exception as err:
            raise APIException(str(err))
