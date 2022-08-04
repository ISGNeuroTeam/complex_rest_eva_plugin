from eva_plugin.pg_connector import  PGConnector, flat_to_list, flat_to_set, row_to_obj, QueryError


class DatabaseConnector:
    def __init__(self):
        self.pg = PGConnector()

    # __CATALOGS__ #############################################################

    def check_catalog_exists(self, name):
        catalog_id = self.pg.execute_query("SELECT id FROM catalog WHERE name = %s;", params=(name,))
        return catalog_id

    def get_catalogs_count(self):
        count = self.pg.execute_query("SELECT COUNT(id) FROM catalog;")
        return count[0]

    def get_catalogs_data(self, *, limit, offset):
        return self.pg.execute_query("SELECT id, name FROM catalog ORDER BY id limit %s offset %s;",
                                  params=(limit, offset), fetchall=True, as_obj=True)

    def add_catalog(self, *, name, content):
        if self.check_catalog_exists(name):
            raise QueryError(f'catalog {name} already exists')
        catalog_id = self.pg.execute_query("INSERT INTO catalog (name, content) VALUES (%s, %s) RETURNING id;",
                                        params=(name, content), with_commit=True)
        return catalog_id

    def update_catalog(self, *, catalog_id, name, content):
        with self.pg.transaction('update_catalog_data') as conn:
            if name:
                self.pg.execute_query("UPDATE catalog SET name = %s WHERE id = %s;",
                                   conn=conn, params=(name, catalog_id), with_fetch=False)
            if content:
                self.pg.execute_query("UPDATE catalog SET content = %s WHERE id = %s;",
                                   conn=conn, params=(content, catalog_id), with_fetch=False)
        return catalog_id

    def get_catalog(self, catalog_id):
        return self.pg.execute_query("SELECT * FROM catalog WHERE id = %s;",
                                  params=(catalog_id,), as_obj=True)

    def delete_catalog(self, catalog_id):
        self.pg.execute_query("DELETE FROM catalog WHERE id = %s;",
                           params=(catalog_id,), with_commit=True, with_fetch=False)
        return catalog_id


db = DatabaseConnector()