from eva_plugin.pg_connector import  PGConnector, flat_to_list, flat_to_set, QueryError


class DatabaseConnector:
    def __init__(self):
        self.pg = PGConnector()

    # __GROUPS__ ###################################################################

    def check_group_exists(self, group_name):
        group_id = self.pg.execute_query('SELECT id FROM "group" WHERE name = %s;', params=(group_name,))
        return group_id

    def get_groups_data(self, *, user_id=None, names_only=False):
        if user_id:
            groups = self.pg.execute_query('SELECT * FROM "group" WHERE id IN '
                                           '(SELECT group_id FROM user_group WHERE user_id = %s);',
                                           fetchall=True, params=(user_id,), as_obj=True)
        else:
            groups = self.pg.execute_query('SELECT * FROM "group";', fetchall=True, as_obj=True)

        if names_only:
            groups = [g['name'] for g in groups]
        else:
            for group in groups:
                users = self.pg.execute_query('SELECT name FROM "user" WHERE id IN '
                                              '(SELECT user_id FROM user_group WHERE group_id = %s);',
                                              params=(group.id,), fetchall=True)
                users = flat_to_list(users)
                group['users'] = users

                dashboards = self.pg.execute_query("SELECT name FROM dash WHERE id IN "
                                                   "(SELECT dash_id FROM dash_group WHERE group_id = %s);",
                                                   params=(group.id,), fetchall=True)
                dashboards = flat_to_list(dashboards)
                group['dashs'] = dashboards

                indexes = self.pg.execute_query("SELECT name FROM index WHERE id IN "
                                                "(SELECT index_id FROM index_group WHERE group_id = %s);",
                                                params=(group.id,), fetchall=True)
                indexes = flat_to_list(indexes)
                group['indexes'] = indexes
        return groups

    def get_group_data(self, group_id):
        group = self.pg.execute_query('SELECT * FROM "group" WHERE id = %s;',
                                      params=(group_id,), as_obj=True)
        if not group:
            raise ValueError(f'group with id={group_id} is not exists')

        users = self.pg.execute_query('SELECT name FROM "user" WHERE id IN '
                                      '(SELECT user_id FROM user_group WHERE group_id = %s);',
                                      params=(group.id,), fetchall=True)
        users = flat_to_list(users)
        group['users'] = users

        dashboards = self.pg.execute_query("SELECT name FROM dash WHERE id IN "
                                           "(SELECT dash_id FROM dash_group WHERE group_id = %s);",
                                           params=(group.id,), fetchall=True)
        dashboards = flat_to_list(dashboards)
        group['dashs'] = dashboards

        indexes = self.pg.execute_query("SELECT name FROM index WHERE id IN "
                                        "(SELECT index_id FROM index_group WHERE group_id = %s);",
                                        params=(group.id,), fetchall=True)
        indexes = flat_to_list(indexes)
        group['indexes'] = indexes
        return group

    def add_group(self, *, name, color, users=None, indexes=None, dashs=None):
        if self.check_group_exists(name):
            raise QueryError(f'group {name} already exists')

        with self.pg.transaction('add_group_data') as conn:
            group_id = self.pg.execute_query('INSERT INTO "group" (name, color) VALUES (%s, %s) RETURNING id;',
                                             conn=conn, params=(name, color))
            if users:
                for user in users:
                    self.pg.execute_query('INSERT INTO user_group (user_id, group_id) '
                                          'VALUES ((SELECT id FROM "user" WHERE name = %s), %s);',
                                          conn=conn, params=(user, group_id,), with_fetch=False)
            if indexes:
                for index in indexes:
                    self.pg.execute_query("INSERT INTO index_group (index_id, group_id) "
                                          "VALUES ((SELECT id FROM index WHERE name = %s), %s);",
                                          conn=conn, params=(index, group_id,), with_fetch=False)

            if dashs:
                for dash in dashs:
                    self.pg.execute_query("INSERT INTO dash_group (dash_id, group_id) "
                                          "VALUES ((SELECT id FROM dash WHERE name = %s), %s);",
                                          conn=conn, params=(dash, group_id,), with_fetch=False)
        return group_id

    def update_group(self, *, group_id, name, color, users=None, indexes=None, dashs=None):
        if name:
            self.pg.execute_query('UPDATE "group" SET name = %s WHERE id = %s;',
                                  params=(name, group_id), with_commit=True, with_fetch=False)
        if color:
            self.pg.execute_query('UPDATE "group" SET color = %s WHERE id = %s;',
                                  params=(color, group_id), with_commit=True, with_fetch=False)

        if isinstance(users, list):
            current_users = self.pg.execute_query('SELECT name FROM "user" WHERE id IN '
                                                  '(SELECT user_id FROM user_group WHERE group_id = %s);',
                                                  params=(group_id,), fetchall=True)
            current_users = flat_to_set(current_users)
            target_users = set(users)

            users_for_add = target_users - current_users
            users_for_delete = tuple(current_users - target_users)

            with self.pg.transaction('update_group_users') as conn:
                for user in users_for_add:
                    self.pg.execute_query('INSERT INTO user_group (user_id, group_id) '
                                          'VALUES ((SELECT id FROM "user" WHERE name = %s), %s);',
                                          conn=conn, params=(user, group_id,), with_fetch=False)
                if users_for_delete:
                    self.pg.execute_query('DELETE FROM user_group WHERE user_id IN '
                                          '(SELECT id FROM "user" WHERE name IN %s) AND group_id = %s;',
                                          conn=conn, params=(users_for_delete, group_id), with_fetch=False)

        if isinstance(indexes, list):
            current_indexes = self.pg.execute_query("SELECT name FROM index WHERE id IN "
                                                    "(SELECT index_id FROM index_group WHERE group_id = %s);",
                                                    params=(group_id,), fetchall=True)
            current_indexes = flat_to_set(current_indexes)
            target_indexes = set(indexes)

            indexes_for_add = target_indexes - current_indexes
            indexes_for_delete = tuple(current_indexes - target_indexes)

            with self.pg.transaction('update_group_indexes') as conn:
                for index in indexes_for_add:
                    self.pg.execute_query("INSERT INTO index_group (index_id, group_id) "
                                          "VALUES ((SELECT id FROM index WHERE name = %s), %s);",
                                          conn=conn, params=(index, group_id,), with_fetch=False)
                if indexes_for_delete:
                    self.pg.execute_query("DELETE FROM index_group WHERE index_id IN "
                                          "(SELECT id FROM index WHERE name IN %s) AND group_id = %s;",
                                          conn=conn, params=(indexes_for_delete, group_id), with_fetch=False)

        if isinstance(dashs, list):
            current_dashs = self.pg.execute_query("SELECT name FROM dash WHERE id IN "
                                                  "(SELECT dash_id FROM dash_group WHERE group_id = %s);",
                                                  params=(group_id,), fetchall=True)
            current_dashs = flat_to_set(current_dashs)
            target_dashs = set(dashs)

            dashs_for_add = target_dashs - current_dashs
            dashs_for_delete = tuple(current_dashs - target_dashs)

            with self.pg.transaction('update_group_dashs') as conn:
                for dash in dashs_for_add:
                    self.pg.execute_query("INSERT INTO dash_group (dash_id, group_id) "
                                          "VALUES ((SELECT id FROM dash WHERE name = %s), %s);",
                                          conn=conn, params=(dash, group_id,), with_fetch=False)
                if dashs_for_delete:
                    self.pg.execute_query("DELETE FROM dash_group WHERE dash_id IN "
                                          "(SELECT id FROM index WHERE name IN %s) AND group_id = %s;",
                                          conn=conn, params=(dashs_for_delete, group_id), with_fetch=False)
        return group_id

    def delete_group(self, group_id):
        self.pg.execute_query('DELETE FROM "group" WHERE id = %s;', params=(group_id,),
                              with_commit=True, with_fetch=False)
        return group_id


db = DatabaseConnector()
