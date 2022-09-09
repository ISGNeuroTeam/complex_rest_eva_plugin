import logging
from contextlib import contextmanager
from typing import Any, Dict
import psycopg2
from psycopg2.pool import PoolError
from psycopg2.pool import SimpleConnectionPool
from asyncio import sleep
from eva_plugin.settings import ini_config


class QueryError(Exception):
    pass


def flat_to_set(arr):
    return {i[0] for i in arr} if arr else set()


def flat_to_list(arr):
    return [i[0] for i in arr] if arr else list()


class ObjectDict(Dict[str, Any]):
    """Makes a dictionary behave like an object, with attribute-style access. Taken from tornado.util
    """

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value


def row_to_obj(row, cur):
    """Convert a SQL row to an object supporting dict and attribute access."""
    obj = ObjectDict()
    for val, desc in zip(row, cur.description):
        obj[desc.name] = val
    return obj


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class PGConnector(metaclass=Singleton):
    """
    Postgres connector class. Singleton. Makes query to database
    """

    def __init__(self):
        self.pool = SimpleConnectionPool(1, 10, **ini_config['db_conf'])
        self.logger = logging.getLogger('pg_connector')

    @contextmanager
    def transaction(self, name="transaction", **kwargs):
        options = {
            "isolation_level": kwargs.get("isolation_level", None),
            "readonly": kwargs.get("readonly", None),
            "deferrable": kwargs.get("deferrable", None),
        }
        while True:
            try:
                conn = self.pool.getconn()
            except PoolError:
                sleep(0.1)
            else:
                break

        try:
            conn.set_session(**options)
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Transaction {name} error: {e}")
            raise RuntimeError(f"Transaction {name} failed")
        finally:
            conn.reset()
            self.pool.putconn(conn)

    def execute_query(self, query, conn=None, params=None, with_commit=False,
                      with_fetch=True, as_obj=False, fetchall=False):
        fetch_result = None

        if not conn:
            with_transaction = False
            while True:
                try:
                    conn = self.pool.getconn()
                except PoolError:
                    sleep(0.1)
                else:
                    break
        else:
            with_transaction = True
        self.logger.debug('Connection: %s' % conn)
        cur = conn.cursor()

        try:
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
            if with_fetch:
                if fetchall:
                    fetch_result = cur.fetchall()
                    if as_obj:
                        fetch_result = [row_to_obj(row, cur) for row in fetch_result]
                else:
                    fetch_result = cur.fetchone()
                    if as_obj and fetch_result:
                        fetch_result = row_to_obj(fetch_result, cur)
            if with_commit:
                conn.commit()
        except psycopg2.OperationalError as err:
            self.logger.error(f'SQL Error: {err}')
        else:
            return fetch_result
        finally:
            cur.close()
            if not with_transaction:
                self.pool.putconn(conn)
