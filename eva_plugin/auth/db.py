from eva_plugin.pg_connector import  PGConnector, flat_to_list, flat_to_set, QueryError


class DatabaseConnector:
    def __init__(self):
        self.pg = PGConnector()

    def get_user_tokens(self, user_id):
        tokens = self.pg.execute_query("SELECT token FROM session WHERE user_id = %s;",
                                    params=(user_id,), fetchall=True)
        tokens = flat_to_set(tokens)
        return tokens

    def get_auth_data(self, user_id):
        login_pass = self.pg.execute_query('SELECT name, password FROM "user" WHERE id = %s;',
                                        params=(user_id,), as_obj=True)
        return login_pass

    def add_session(self, *, user_id, token, expired_date):
        self.pg.execute_query("INSERT INTO session (token, user_id, expired_date) VALUES (%s, %s, %s);",
                           params=(token, user_id, expired_date), with_commit=True, with_fetch=False)

    # __USERS__ #######################################################################

    def check_user_exists(self, name):
        user = self.pg.execute_query('SELECT * FROM "user" WHERE name = %s;',
                                  params=(name,), as_obj=True)
        return user

    def get_users_data(self, *, user_id=None, names_only=False):
        if user_id:
            users = self.pg.execute_query('SELECT id, name FROM "user" WHERE id = %s;',
                                       params=(user_id,), fetchall=True, as_obj=True)
        else:
            users = self.pg.execute_query('SELECT id, name FROM "user";', fetchall=True, as_obj=True)
        if names_only:
            users = [u['name'] for u in users]
        else:
            for user in users:
                user_roles = self.pg.execute_query("SELECT name FROM role WHERE id IN "
                                                "(SELECT role_id FROM user_role WHERE user_id = %s);",
                                                params=(user.id,), fetchall=True)
                user_roles = flat_to_list(user_roles)
                user['roles'] = user_roles

                user_groups = self.pg.execute_query('SELECT name FROM "group" WHERE id IN '
                                                 '(SELECT group_id FROM user_group WHERE user_id = %s);',
                                                 params=(user.id,), fetchall=True)
                user_groups = flat_to_list(user_groups)
                user['groups'] = user_groups
        return users

    def get_user_data(self, *, user_id):
        user_data = self.pg.execute_query('SELECT id, name FROM "user" WHERE id = %s;',
                                       params=(user_id,), as_obj=True)
        user_roles = self.pg.execute_query("SELECT name FROM role WHERE id IN "
                                        "(SELECT role_id FROM user_role WHERE user_id = %s);",
                                        params=(user_id,), fetchall=True)
        user_roles = flat_to_list(user_roles)
        user_data['roles'] = user_roles

        user_groups = self.pg.execute_query('SELECT name FROM "group" WHERE id IN '
                                         '(SELECT group_id FROM user_group WHERE user_id = %s);',
                                         params=(user_data.id,), fetchall=True)
        user_groups = flat_to_list(user_groups)
        user_data['groups'] = user_groups

        return user_data

    def add_user(self, *, name, password, roles, groups):
        if self.check_user_exists(name):
            raise QueryError(f'user {name} already exists')

        with self.pg.transaction('add_user_data') as conn:
            user_id = self.pg.execute_query('INSERT INTO "user" (name, password) VALUES (%s, %s) RETURNING id;',
                                         conn=conn, params=(name, password))
            if roles:
                for role in roles:
                    self.pg.execute_query("INSERT INTO user_role (role_id, user_id) "
                                       "VALUES ((SELECT id FROM role WHERE name = %s), %s);",
                                       conn=conn, params=(role, user_id), with_fetch=False)
            if groups:
                for group in groups:
                    self.pg.execute_query('INSERT INTO user_group (group_id, user_id) '
                                       'VALUES ((SELECT id FROM "group" WHERE name = %s), %s);',
                                       conn=conn, params=(group, user_id), with_fetch=False)
        return user_id

    def update_user(self, *, user_id, name, password, roles=None, groups=None):
        if name:
            self.pg.execute_query('UPDATE "user" SET name = %s WHERE id = %s;', params=(name, user_id),
                               with_commit=True, with_fetch=False)
        if password:
            self.pg.execute_query('UPDATE "user" SET password = %s WHERE id = %s;', params=(password, user_id),
                               with_commit=True, with_fetch=False)

        if isinstance(roles, list):
            current_roles = self.pg.execute_query("SELECT name FROM role WHERE id IN "
                                               "(SELECT role_id FROM user_role WHERE user_id = %s);",
                                               params=(user_id,), fetchall=True)
            current_roles = flat_to_set(current_roles)
            target_roles = set(roles)

            roles_for_add = target_roles - current_roles
            roles_for_delete = tuple(current_roles - target_roles)

            with self.pg.transaction('update_user_roles') as conn:
                for role in roles_for_add:
                    self.pg.execute_query("INSERT INTO user_role (role_id, user_id) "
                                       "VALUES ((SELECT id FROM role WHERE name = %s), %s);",
                                       conn=conn, params=(role, user_id,), with_fetch=False)
                if roles_for_delete:
                    self.pg.execute_query("DELETE FROM user_role WHERE role_id IN (SELECT id FROM role WHERE name IN %s) "
                                       "AND user_id = %s;",
                                       conn=conn, params=(roles_for_delete, user_id,), with_fetch=False)

        if isinstance(groups, list):
            current_groups = self.pg.execute_query('SELECT name FROM "group" WHERE id IN '
                                                '(SELECT group_id FROM user_group WHERE user_id = %s);',
                                                params=(user_id,), fetchall=True)
            current_groups = flat_to_set(current_groups)
            target_groups = set(groups)

            groups_for_add = target_groups - current_groups
            groups_for_delete = tuple(current_groups - target_groups)

            with self.pg.transaction('update_user_groups') as conn:
                for group in groups_for_add:
                    group_id = self.pg.execute_query('SELECT id FROM "group" WHERE name = %s;',
                                                  conn=conn, params=(group,))
                    self.pg.execute_query("INSERT INTO user_group (user_id, group_id) VALUES (%s, %s);",
                                       conn=conn, params=(user_id, group_id,), with_fetch=False)
                if groups_for_delete:
                    self.pg.execute_query('DELETE FROM user_group WHERE user_id = %s AND group_id IN '
                                       '(SELECT id FROM "group" WHERE name in %s);',
                                       conn=conn, params=(user_id, groups_for_delete,), with_fetch=False)
        return user_id

    def delete_user(self, user_id):
        self.pg.execute_query('DELETE FROM "user" WHERE id = %s;', params=(user_id,),
                           with_commit=True, with_fetch=False)
        return user_id

    def get_user_setting(self, user_id):
        user_data = self.pg.execute_query('SELECT id, setting FROM "user_settings" WHERE id = %s;',
                                       params=(user_id,), as_obj=True)
        if user_data:
            return user_data
        else:
            return {'id': user_id, 'setting': ''}

    def update_user_setting(self, user_id, setting):
        with self.pg.transaction('update_user_setting') as conn:
            self.logger.debug(('DELETE FROM "user_settings" WHERE id = %s;' % user_id))
            self.pg.execute_query('DELETE FROM "user_settings" WHERE id = %s;', conn=conn, params=(user_id,),
                               with_fetch=False, with_commit=True)
            self.logger.debug('INSERT INTO "user_settings" (id, setting) VALUES (%s, %s);' % (user_id, str(setting)))
            self.pg.execute_query('INSERT INTO "user_settings" (id, setting) VALUES (%s, %s);', conn=conn,
                               params=(user_id, str(setting)), with_fetch=False, with_commit=True)
        return user_id

    # __ROLES__ #####################################################################

    def check_role_exists(self, role_name):
        role_id = self.pg.execute_query("SELECT id FROM role WHERE name = %s;", params=(role_name,))
        return role_id

    def get_roles_data(self, user_id=None, names_only=False, with_relations=False):
        if user_id:
            roles = self.pg.execute_query("SELECT * FROM role WHERE id IN "
                                       "(SELECT role_id FROM user_role WHERE user_id = %s);",
                                       fetchall=True, params=(user_id,), as_obj=True)
        else:
            roles = self.pg.execute_query("SELECT * FROM role;", fetchall=True, as_obj=True)
        if names_only:
            roles = [r['name'] for r in roles]
        else:
            for role in roles:
                permissions = self.pg.execute_query("SELECT name FROM permission WHERE id IN "
                                                 "(SELECT permission_id FROM role_permission WHERE role_id = %s);",
                                                 params=(role.id,), fetchall=True)
                permissions = flat_to_list(permissions)
                role['permissions'] = permissions
                users = self.pg.execute_query('SELECT name FROM "user" WHERE id in '
                                           '(SELECT user_id FROM user_role WHERE role_id = %s)',
                                           params=(role.id,), fetchall=True)
                users = flat_to_list(users)
                role['users'] = users

            if with_relations:
                all_permissions = self.get_permissions_data(names_only=True)
                all_users = self.get_users_data(names_only=True)
                roles = {'roles': roles, 'permissions': all_permissions, 'users': all_users}
        return roles

    def get_role_data(self, role_id):
        role = self.pg.execute_query("SELECT * FROM role WHERE id = %s;",
                                  params=(role_id,), as_obj=True)
        permissions = self.pg.execute_query("SELECT name FROM permission WHERE id IN "
                                         "(SELECT permission_id FROM role_permission WHERE role_id = %s);",
                                         params=(role.id,), fetchall=True)
        permissions = flat_to_list(permissions)
        role['permissions'] = permissions
        users = self.pg.execute_query('SELECT name FROM "user" WHERE id in '
                                   '(SELECT user_id FROM user_role WHERE role_id = %s)',
                                   params=(role.id,), fetchall=True)
        users = flat_to_list(users)
        role['users'] = users
        return role

    def add_role(self, *, name, users, permissions):
        if self.check_role_exists(name):
            raise QueryError(f'role {name} already exists')

        with self.pg.transaction('add_role_data') as conn:
            role_id = self.pg.execute_query("INSERT INTO role (name) VALUES (%s) RETURNING id;",
                                         conn=conn, params=(name,))
            if users:
                for user in users:
                    self.pg.execute_query('INSERT INTO user_role (user_id, role_id) '
                                       'VALUES ((SELECT id FROM "user" WHERE name = %s), %s);',
                                       conn=conn, params=(user, role_id,), with_fetch=False)
            if permissions:
                for permission in permissions:
                    self.pg.execute_query("INSERT INTO role_permission (permission_id, role_id) "
                                       "VALUES ((SELECT id FROM permission WHERE name = %s), %s);",
                                       conn=conn, params=(permission, role_id,), with_fetch=False)
        return role_id

    def update_role(self, *, role_id, name, users=None, permissions=None):
        if name:
            self.pg.execute_query("UPDATE role SET name = %s WHERE id = %s;", params=(name, role_id),
                               with_commit=True, with_fetch=False)
        if isinstance(users, list):
            current_users = self.pg.execute_query('SELECT name FROM "user" WHERE id IN '
                                               '(SELECT user_id FROM user_role WHERE role_id = %s);',
                                               params=(role_id,), fetchall=True)
            current_users = flat_to_set(current_users)
            target_users = set(users)

            users_for_add = target_users - current_users
            users_for_delete = tuple(current_users - target_users)

            with self.pg.transaction('update_role_users') as conn:

                for user in users_for_add:
                    self.pg.execute_query('INSERT INTO user_role (user_id, role_id) '
                                       'VALUES ((SELECT id FROM "user" WHERE name = %s), %s);',
                                       conn=conn, params=(user, role_id,), with_fetch=False)
                if users_for_delete:
                    self.pg.execute_query('DELETE FROM user_role WHERE user_id IN '
                                       '(SELECT id FROM "user" WHERE name IN %s) AND role_id = %s;',
                                       conn=conn, params=(users_for_delete, role_id), with_fetch=False)

        if isinstance(permissions, list):
            current_permissions = self.pg.execute_query("SELECT name FROM permission WHERE id IN "
                                                     "(SELECT permission_id FROM role_permission WHERE role_id = %s);",
                                                     params=(role_id,), fetchall=True)
            current_permissions = flat_to_set(current_permissions)
            target_permissions = set(permissions)

            permissions_for_add = target_permissions - current_permissions
            permissions_for_delete = tuple(current_permissions - target_permissions)

            with self.pg.transaction('update_role_permissions') as conn:

                for permission in permissions_for_add:
                    self.pg.execute_query("INSERT INTO role_permission (permission_id, role_id) "
                                       "VALUES ((SELECT id FROM permission WHERE name = %s), %s);",
                                       conn=conn, params=(permission, role_id,), with_fetch=False)
                if permissions_for_delete:
                    self.pg.execute_query("DELETE FROM role_permission WHERE permission_id IN "
                                       "(SELECT id FROM permission WHERE name IN %s) AND role_id = %s;",
                                       conn=conn, params=(permissions_for_delete, role_id), with_fetch=False)
        return role_id

    def get_role(self, role_id):
        role_data = self.pg.execute_query("SELECT * FROM role WHERE id = %s;", params=(role_id,), as_obj=True)
        return role_data

    def delete_role(self, role_id):
        self.pg.execute_query("DELETE FROM role WHERE id = %s;", params=(role_id,),
                           with_commit=True, with_fetch=False)
        return role_id

 # __PERMISSIONS__ ###############################################################

    def check_permission_exists(self, permission_name):
        permission_id = self.execute_query("SELECT id from permission WHERE name = %s;",
                                           params=(permission_name,))
        return permission_id

    def get_permissions_data(self, *, user_id=None, names_only=False):
        if user_id:
            user_roles = self.get_roles_data(user_id=user_id, names_only=True)
            permissions = list()
            for role in user_roles:
                role_id = self.execute_query("SELECT id FROM role WHERE name = %s;", params=(role,))
                role_permissions = self.execute_query("SELECT * FROM permission WHERE id IN "
                                                      "(SELECT permission_id FROM role_permission WHERE role_id = %s);",
                                                      params=(role_id,), fetchall=True, as_obj=True)
                permissions.extend(role_permissions)
            permissions = list({v['id']: v for v in permissions}.values())
        else:
            permissions = self.execute_query("SELECT * FROM permission;", fetchall=True, as_obj=True)
        if names_only:
            permissions = [p['name'] for p in permissions]
        else:
            for permission in permissions:
                roles = self.execute_query("SELECT name FROM role WHERE id IN "
                                           "(SELECT role_id FROM role_permission WHERE permission_id = %s);",
                                           params=(permission.id,), fetchall=True)
                roles = flat_to_list(roles)
                permission['roles'] = roles
        return permissions

    def get_permission_data(self, permission_id):
        permission = self.execute_query("SELECT * FROM permission WHERE id = %s;",
                                        params=(permission_id,), as_obj=True)
        roles = self.execute_query("SELECT name FROM role WHERE id IN "
                                   "(SELECT role_id FROM role_permission WHERE permission_id = %s);",
                                   params=(permission.id,), fetchall=True)
        roles = flat_to_list(roles)
        permission['roles'] = roles
        return permission

    def add_permission(self, *, name, roles):
        if self.check_permission_exists(name):
            raise QueryError(f'group {name} already exists')

        with self.transaction('add_permission_data') as conn:
            permission_id = self.execute_query("INSERT INTO permission (name) VALUES (%s) RETURNING id;",
                                               conn=conn, params=(name,))
            if roles:
                for role in roles:
                    self.execute_query("INSERT INTO role_permission (role_id, permission_id) "
                                       "VALUES ((SELECT id FROM role WHERE name = %s), %s);",
                                       conn=conn, params=(role, permission_id,), with_fetch=False)
        return permission_id

    def update_permission(self, *, permission_id, name, roles=None):
        if name:
            self.execute_query("UPDATE permission SET name = %s WHERE id = %s;",
                               params=(name, permission_id), with_commit=True, with_fetch=False)

        if isinstance(roles, list):
            current_roles = self.execute_query("SELECT name FROM role WHERE id IN "
                                               "(SELECT role_id FROM role_permission WHERE permission_id = %s);",
                                               params=(permission_id,), fetchall=True)
            current_roles = flat_to_set(current_roles)
            target_roles = set(roles)

            roles_for_add = target_roles - current_roles
            roles_for_delete = tuple(current_roles - target_roles)

            with self.transaction('update_group_users') as conn:
                for role in roles_for_add:
                    self.execute_query("INSERT INTO role_permission (role_id, permission_id) "
                                       "VALUES ((SELECT id FROM role WHERE name = %s), %s);",
                                       conn=conn, params=(role, permission_id,), with_fetch=False)
                if roles_for_delete:
                    self.execute_query("DELETE FROM role_permission WHERE role_id IN "
                                       "(SELECT id FROM role WHERE name IN %s) AND permission_id = %s;",
                                       conn=conn, params=(roles_for_delete, permission_id), with_fetch=False)
        return permission_id

    def delete_permission(self, permission_id):
        self.execute_query("DELETE FROM permission WHERE id = %s;", params=(permission_id,),
                           with_commit=True, with_fetch=False)
        return permission_id


db = DatabaseConnector()
