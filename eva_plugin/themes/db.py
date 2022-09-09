import logging

from eva_plugin.pg_connector import  PGConnector, flat_to_list, flat_to_set, row_to_obj, QueryError


logger = logging.getLogger('eva_plugin')


class DatabaseConnector:

    logger = logger

    def __init__(self):
        self.pg = PGConnector()

    def get_themes_data(self, *, limit, offset):
        self.logger.debug(f'SELECT name FROM theme ORDER BY name limit {limit} offset {offset};')
        return self.pg.execute_query("SELECT name FROM theme ORDER BY name limit %s offset %s;",
                                     params=list([limit, offset]), fetchall=True, as_obj=True)

    def get_theme(self, theme_name):
        self.logger.debug(f'SELECT * FROM theme WHERE name = "{theme_name}";')
        return self.pg.execute_query("SELECT * FROM theme WHERE name = %s;",
                                     params=list([theme_name]), as_obj=True)

    def check_theme_exists(self, theme_name):
        self.logger.debug(f'SELECT name FROM theme WHERE name = "{theme_name}";')
        return self.pg.execute_query("SELECT name FROM theme WHERE name = %s;", params=list([theme_name]))

    def add_theme(self, *, theme_name, content):
        if self.check_theme_exists(theme_name):
            raise Exception(f'theme "{theme_name}" already exists')
        self.logger.debug(f'INSERT INTO theme (name, content) VALUES ("{theme_name}", "{content}") RETURNING content;')
        theme = self.pg.execute_query("INSERT INTO theme (name, content) VALUES (%s, %s) RETURNING content;",
                                      params=list([theme_name, content]), with_commit=True)
        return theme

    def delete_theme(self, theme_name):
        self.logger.debug(f'DELETE FROM theme WHERE name = "{theme_name}";')
        self.pg.execute_query("DELETE FROM theme WHERE name = %s;",
                              params=list([theme_name]), with_commit=True, with_fetch=False)
        return theme_name

db = DatabaseConnector()
