import logging

from .connection import AsyncConnection


logger = logging.getLogger('stdout')


class DataBase:
    """
    >>> engine = AsyncConnection('postgresql://postgres:postgres@localhost:5432/databasename')
    >>> async with DataBase(engine) as db:
    ...     await db.execute("SELECT pump_data();")
    ...     await db.fetchall("SELECT 1")
    """

    def __init__(self, engine: AsyncConnection) -> None:
        self._engine = engine
        self._connection = None

    async def connect(self):
        self._connection = await self._engine.get_connection()
        return self

    async def close(self):
        if not self._connection:
            raise RuntimeError('You must use the .connect() first')
        await self._connection.close()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        try:
            await self._connection.commit()
        except Exception as e:
            logger.error(e)
        finally:
            await self.close()

    async def execute(self, sql) -> None:
        if not self._connection:
            raise RuntimeError('You must use the .connect() first')
        await self._engine.execute(self._connection, sql)

    async def fetchall(self, sql: str) -> list:
        return await self._engine.fetchall(self._connection, sql)

    @property
    def columns(self):
        return self._engine.columns
