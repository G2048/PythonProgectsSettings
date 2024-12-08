from abc import ABC, abstractmethod

import psycopg
from psycopg.rows import dict_row

# class AsyncDataBase:
#     def __init__(self, pg_dsn: str) -> None:
#         self.pg_dsn = pg_dsn

#     async def __ainit__(self):
#         self._connect = await psycopg.AsyncConnection.connect(self.pg_dsn)

#     def __await__(self):
#         return self.__ainit__().__await__()

#     async def execute(self, sql):
#         cursor = await self._connect.execute(sql)
#         res = await cursor.fetchall()
#         return res

#     async def close(self):
#         await self._connect.close()

#     async def __aenter__(self):
#         return self

#     async def __aexit__(self, exc_type, exc, tb):
#         await self


class AsyncConnection(ABC):
    @abstractmethod
    async def get_connection(self):
        pass

    @abstractmethod
    async def execute(self, connection, sql) -> None:
        pass

    @abstractmethod
    async def fetchall(self, connection, sql) -> list:
        pass

    @property
    @abstractmethod
    def columns(self) -> list:
        pass


class PsycopgAsyncConnection(AsyncConnection):
    __slots__ = ('_connect', '_pg_dsn', '_cursor')

    def __init__(self, pg_dsn: str) -> None:
        self._connect = psycopg.AsyncConnection
        self._pg_dsn = pg_dsn
        self._cursor = None
        self._connect.autocommit = True

    async def get_connection(self):
        conn_args = {
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 5,
            'keepalives_count': 5,
            'connect_timeout': 600,
        }
        return await self._connect.connect(
            conninfo=self._pg_dsn,
            row_factory=dict_row,
            **conn_args,
        )

    async def execute(self, connection, sql):
        await connection.execute(sql)

    async def fetchall(self, connection, sql):
        self._cursor = await connection.execute(sql)
        return await self._cursor.fetchall()

    @property
    def columns(self) -> list:
        if not self._cursor:
            raise RuntimeError('You must use the .get_connection() first')
        return self._cursor.description
