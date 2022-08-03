from eva_plugin.pg_connector import  PGConnector, flat_to_list, flat_to_set


class DatabaseConnector:
    def __init__(self):
        self.pg = PGConnector()

  # __DASHBOARDS__ ###############################################################

    def check_dash_exists(self, dash_name):
        dash_id = self.execute_query("SELECT id FROM dash WHERE name = %s;", params=(dash_name,))
        return dash_id

    def get_dashs_data(self, *, group_id=None, names_only=False):
        if group_id:
            dashs = self.execute_query("SELECT id, name, body, round(extract(epoch from modified)) as modified "
                                       "FROM dash WHERE id IN (SELECT dash_id FROM dash_group WHERE group_id = %s);",
                                       params=(group_id,), fetchall=True, as_obj=True)
        else:
            dashs = self.execute_query("SELECT id, name, body, round(extract(epoch from modified)) as modified "
                                       "FROM dash;", fetchall=True, as_obj=True)

        if names_only:
            dashs = [d['name'] for d in dashs]
        else:
            for dash in dashs:
                groups = self.execute_query('SELECT name FROM "group" WHERE id IN '
                                            '(SELECT group_id FROM dash_group WHERE dash_id = %s);',
                                            params=(dash.id,), fetchall=True, as_obj=True)
                groups = list({v['name']: v for v in groups}.values())
                dash['groups'] = groups
        return dashs

    def get_dash_data(self, dash_id):
        dash_data = self.execute_query("SELECT id, name, body, round(extract(epoch from modified)) as modified "
                                       "FROM dash WHERE id = %s;", params=(dash_id,), as_obj=True)
        if not dash_data:
            raise ValueError(f'Dash with id={dash_id} is not exists')

        groups = self.execute_query('SELECT name FROM "group" WHERE id IN '
                                    '(SELECT group_id FROM dash_group WHERE dash_id = %s);',
                                    params=(dash_id,), fetchall=True)
        groups = flat_to_list(groups)
        dash_data['groups'] = groups
        return dash_data

    def get_dash_data_by_name(self, dash_name, dash_group):
        dash_data = self.execute_query("SELECT id, name, body, round(extract(epoch from modified)) as modified "
                                       "FROM dash WHERE name = %s LIMIT 1;", params=(dash_name,), as_obj=True)
        if not dash_data:
            raise ValueError(f'Dash with name={dash_name} is not exists')

        groups = self.execute_query('SELECT name FROM "group" WHERE id IN '
                                    '(SELECT group_id FROM dash_group WHERE dash_id = %s);',
                                    params=(dash_data['id'],), fetchall=True)
        groups = flat_to_list(groups)
        dash_data['groups'] = groups
        return dash_data

    def add_dash(self, *, name, body, groups=None):
        dash_id = self.check_dash_exists(dash_name=name)
        if dash_id:
            raise QueryError(f'dash with name={name} is already exists')

        with self.transaction('add_dashboard_data') as conn:
            dash = self.execute_query("INSERT INTO dash (name, body) VALUES (%s, %s) "
                                      "RETURNING id, round(extract(epoch from modified)) as modified;",
                                      conn=conn, params=(name, body,), as_obj=True)
            if isinstance(groups, list):
                for group in groups:
                    self.execute_query('INSERT INTO dash_group (group_id, dash_id) '
                                       'VALUES ((SELECT id FROM "group" WHERE name = %s), %s);',
                                       conn=conn, params=(group, dash.id,), with_fetch=False)
        return dash.id, dash.modified

    def update_dash(self, *, dash_id, name, body, groups=None):
        dash_name = self.execute_query("SELECT name FROM dash WHERE id = %s;", params=(dash_id,))
        if not dash_name:
            raise QueryError(f'dash with id={dash_id} is not exists')

        with self.transaction('update_dash_data') as conn:
            dash = self.execute_query("UPDATE dash SET modified = now() WHERE id = %s "
                                      "RETURNING name, round(extract(epoch from modified)) as modified;",
                                      conn=conn, params=(dash_id,), as_obj=True)
            if name:
                self.execute_query("UPDATE dash SET name = %s WHERE id = %s;",
                                   conn=conn, params=(name, dash_id), with_fetch=False)
            if body:
                self.execute_query("UPDATE dash SET body = %s WHERE id = %s;",
                                   conn=conn, params=(body, dash_id), with_fetch=False)

        if isinstance(groups, list):
            current_groups = self.execute_query('SELECT name FROM "group" WHERE id IN '
                                                '(SELECT group_id FROM dash_group WHERE dash_id = %s);',
                                                params=(dash_id,), fetchall=True)
            current_groups = flat_to_set(current_groups)
            target_groups = set(groups)

            groups_for_add = target_groups - current_groups
            groups_for_delete = tuple(current_groups - target_groups)

            with self.transaction('update_dash_groups') as conn:
                for group in groups_for_add:
                    self.execute_query('INSERT INTO dash_group (group_id, dash_id) '
                                       'VALUES ((SELECT id FROM "group" WHERE name = %s), %s);',
                                       conn=conn, params=(group, dash_id,), with_fetch=False)
                if groups_for_delete:
                    self.execute_query('DELETE FROM dash_group  WHERE group_id IN '
                                       '(SELECT id FROM "group" WHERE name IN %s) AND dash_id = %s;',
                                       conn=conn, params=(groups_for_delete, dash_id), with_fetch=False)
        return dash.name, dash.modified

    def delete_dash(self, dash_id):
        self.execute_query("DELETE FROM dash WHERE id = %s;",
                           params=(dash_id,), with_commit=True, with_fetch=False)
        return dash_id




