from eva_plugin.pg_connector import  PGConnector, flat_to_list, flat_to_set, row_to_obj, QueryError


class DatabaseConnector:
    def __init__(self):
        self.pg = PGConnector()

 # __INDEXES___ #################################################################

    def check_index_exists(self, index_name):
        index_id = self.pg.execute_query("SELECT id FROM index WHERE name = %s;", params=(index_name,))
        return index_id

    def get_indexes_data(self, *, user_id=None, names_only=False):
        if user_id:
            user_groups = self.get_groups_data(user_id=user_id)
            indexes = list()

            for group in user_groups:
                group_indexes = self.pg.execute_query("SELECT * FROM index WHERE id IN "
                                                   "(SELECT index_id FROM index_group WHERE group_id = %s);",
                                                   fetchall=True, params=(group.id,), as_obj=True)
                indexes.extend(group_indexes)
            indexes = list({v['id']: v for v in indexes}.values())
        else:
            indexes = self.pg.execute_query('SELECT * FROM index;', fetchall=True, as_obj=True)

        if names_only:
            indexes = [i['name'] for i in indexes]
        else:
            for index in indexes:
                groups = self.pg.execute_query('SELECT name FROM "group" WHERE id IN '
                                            '(SELECT group_id FROM index_group WHERE index_id = %s);',
                                            params=(index.id,), fetchall=True)
                groups = flat_to_list(groups)
                index['groups'] = groups
        return indexes

    def get_index_data(self, index_id):
        index = self.pg.execute_query("SELECT * FROM index WHERE id = %s;",
                                   params=(index_id,), as_obj=True)
        groups = self.pg.execute_query('SELECT name FROM "group" WHERE id IN '
                                    '(SELECT group_id FROM index_group WHERE index_id = %s);',
                                    params=(index.id,), fetchall=True)
        groups = flat_to_list(groups)
        index['groups'] = groups
        return index

    def add_index(self, *, name, groups):
        if self.check_index_exists(name):
            raise QueryError(f'index {name} already exists')

        with self.pg.transaction('add_index_data') as conn:
            index_id = self.pg.execute_query("INSERT INTO index (name) VALUES (%s) RETURNING id;",
                                          conn=conn, params=(name,))
            if groups:
                for group in groups:
                    self.pg.execute_query('INSERT INTO index_group (group_id, index_id) '
                                       'VALUES ((SELECT id FROM "group" WHERE name = %s), %s);',
                                       conn=conn, params=(group, index_id,), with_fetch=False)
        return index_id

    def update_index(self, *, index_id, name, groups=None):
        if name:
            self.pg.execute_query("UPDATE index SET name = %s WHERE id = %s;", params=(name, index_id),
                               with_commit=True, with_fetch=False)
        if isinstance(groups, list):
            current_groups = self.pg.execute_query('SELECT name FROM "group" WHERE id IN '
                                                '(SELECT group_id FROM index_group WHERE index_id = %s);',
                                                params=(index_id,), fetchall=True)
            current_groups = flat_to_set(current_groups)
            target_groups = set(groups)

            groups_for_add = target_groups - current_groups
            groups_for_delete = tuple(current_groups - target_groups)

            with self.pg.transaction('update_index_groups') as conn:
                for group in groups_for_add:
                    self.pg.execute_query('INSERT INTO index_group (group_id, index_id) '
                                       'VALUES ((SELECT id FROM "group" WHERE name = %s), %s);',
                                       conn=conn, params=(group, index_id,), with_fetch=False)
                if groups_for_delete:
                    self.pg.execute_query('DELETE FROM index_group  WHERE group_id IN '
                                       '(SELECT id FROM "group" WHERE name IN %s) AND index_id = %s;',
                                       conn=conn, params=(groups_for_delete, index_id), with_fetch=False)
        return index_id

    def delete_index(self, index_id):
        self.pg.execute_query("DELETE FROM index WHERE id = %s;", params=(index_id,),
                           with_commit=True, with_fetch=False)
        return index_id

db = DatabaseConnector()

