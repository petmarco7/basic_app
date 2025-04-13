import asyncio
import os

import asyncpg
from tenacity import retry, stop_after_attempt, wait_fixed

from .logging_config import logger

database = os.getenv("POSTGRES_DB")
username = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")


class PostgresDatabase:
    host: str | None = None
    port: str | None = None
    username: str | None = None
    password: str | None = None

    dsn: str | None = None

    _pool: asyncpg.Pool | None = None

    def __init__(self, url: str | None = None, **kwargs: tuple) -> None:
        """Initialize the database connection.

        Args:
        ----
            url (str, optional): The URL of the database. Defaults to None.
            **kwargs: The connection parameters like username, password, database, host, and port.

        """
        if url:
            self.dsn = url
            return

        msg = "URL or following connection parameters must be provided: username, password, database."
        assert all([
            kwargs.get("username"),
            kwargs.get("password"),
            kwargs.get("database"),
        ]), msg

        # If the URL is not provided, the connection parameters must be provided
        self.username = kwargs["username"]
        self.password = kwargs["password"]
        self.database = kwargs["database"]
        self.host = kwargs.get("host", "database")
        self.port = kwargs.get("port", 5432)
        self.port = str(self.port)

        self.dsn = self._get_dsn()

    def _get_dsn(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

    def connect(self) -> asyncpg.Connection:
        return asyncio.run(self.aconnect())

    async def aconnect(self) -> asyncpg.Connection:
        """Create a connection pool."""
        try:
            self._pool = await asyncpg.create_pool(
                dsn=self.dsn,
                min_size=5,
                max_size=30,
                max_queries=1000,
                max_inactive_connection_lifetime=60,
                timeout=30,
            )
            logger.info("Postgres connection pool created")
        except Exception as e:
            msg = f"Failed to create the connection pool: {e}"
            logger.error(msg)
            raise

    async def disconnect(self) -> None:
        """Close the connection pool."""
        if self._pool:
            await self._pool.close()
            logger.info("Postgres connection pool disconnected")

    async def _close_connection(self, conn: asyncpg.Connection) -> None:
        """Close the connection.

        Args:
        ----
            conn (asyncpg.Connection): The connection to be closed.

        """
        if self._pool is None:
            await conn.close()
            return

        await self._pool.release(conn)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def get_connection(self) -> asyncpg.Connection:
        """Establish a connection to the database with retry mechanism."""
        if not self._pool:
            try:
                return await asyncpg.connect(self.dsn)
            except Exception as e:
                msg = f"Failed to connect to the database: {e}"
                logger.error(msg)
                raise

        try:
            return await self._pool.acquire()
        except Exception as e:
            msg = f"Failed to acquire a connection from the pool: {e}"
            logger.error(msg)
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def execute(self, query: str, *args: tuple) -> None:
        """Execute a command like creating a table or modifying data.

        Args:
        ----
            query (str): The query to be executed.
            *args: The arguments to be passed to the query.

        """
        conn = await self.get_connection()
        try:
            await conn.execute(query, *args)
        except Exception as e:
            msg = f"Failed to execute the query: {e}"
            logger.error(msg)
            raise
        finally:
            await self._close_connection(conn)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def select(self, query: str, *args: tuple) -> list:
        """Execute a select query and return the result.

        Args:
        ----
            query (str): The query to be executed.
            *args: The arguments to be passed to the query.

        Returns:
        -------
            list: The result of the query.

        """
        conn = await self.get_connection()
        try:
            return await conn.fetch(query, *args)
        except Exception as e:
            msg = f"Failed to execute the query: {e}"
            logger.error(msg)
            raise
        finally:
            await self._close_connection(conn)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def insert(self, query: str, *args: tuple) -> int:
        """Execute an insert command and return the inserted ID.

        Args:
        ----
            query (str): The query to be executed.
            *args: The arguments to be passed to the query.

        Returns:
        -------
            int: The ID of the inserted row.

        """
        conn = await self.get_connection()
        try:
            return await conn.execute(query, *args)
        except Exception as e:
            msg = f"Failed to execute the query: {e}"
            logger.error(msg)
            raise
        finally:
            await self._close_connection(conn)


db = PostgresDatabase(username=username, password=password, database=database)
