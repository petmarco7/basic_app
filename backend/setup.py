import asyncio

from .database import db
from .logging_config import logger


async def main() -> None:
    await db.aconnect()

    # Create a table
    await db.execute("""
        CREATE TABLE IF NOT EXISTS annotations (
            text_id SERIAL PRIMARY KEY,
            text TEXT NOT NULL,
            annotations TEXT NOT NULL
        );
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS texts (
            text_id SERIAL PRIMARY KEY,
            text TEXT NOT NULL,
            annotations TEXT
        ); """)

    query = """INSERT INTO texts (text_id, text)
                VALUES (1, 'Hi, this is Marco and I am a software engineer living in Zurich.')
                ON CONFLICT (text_id) DO NOTHING;
            """

    await db.insert(query)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS searches (
            search_id SERIAL PRIMARY KEY,
            search TEXT NOT NULL
        ); """)


if __name__ == "__main__":
    asyncio.run(main())

    msg = "Setup of database completed successfully!"
    logger.info(msg)
