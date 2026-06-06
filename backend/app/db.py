from contextlib import contextmanager
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

from app.config import settings

pool = ConnectionPool(conninfo=settings.database_url, kwargs={"row_factory": dict_row}, min_size=1, max_size=10)


@contextmanager
def get_conn():
    with pool.connection() as conn:
        yield conn
