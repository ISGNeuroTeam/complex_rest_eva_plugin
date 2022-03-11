from .settings import DB_POOL
from .utils.db_connector import PostgresConnector

db = PostgresConnector(DB_POOL)
