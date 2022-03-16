
# needed for db connection
from plugins.db_connector.connector_singleton import db


class ThemeManager:
    """
    Theme manager is created for interfacing with themes
    """

    @staticmethod
    def get_themes(limit : int, offset : int) -> list[tuple]:
        result = db.get_themes_data(limit=limit, offset=offset)
        return result

    @staticmethod
    def get_theme(theme_name : str) -> tuple[str, str]:
        theme = db.get_theme(theme_name=theme_name)
        return theme

    @staticmethod
    def create_theme(theme_name : str, content : str) -> tuple[str, str]:
        theme = db.add_theme(theme_name=theme_name,
                     content=content)
        return theme

    @staticmethod
    def delete_theme(theme_name : str) -> tuple[str, str]:
        theme = db.get_theme(theme_name=theme_name)
        db.delete_theme(theme_name=theme_name)
        return theme

