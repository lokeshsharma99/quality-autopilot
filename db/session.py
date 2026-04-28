"""
Database Session
================

PostgreSQL database connection for Quality Autopilot.
"""

from os import getenv

from agno.db.postgres import PostgresDb
from agno.knowledge import Knowledge
from agno.knowledge.embedder.ollama import OllamaEmbedder
from agno.vectordb.pgvector import PgVector, SearchType

from db.url import db_url

DB_ID = "quality-autopilot-db"

# Ollama host — inside Docker use host.docker.internal to reach the host machine
OLLAMA_HOST = getenv("OLLAMA_HOST", "http://host.docker.internal:11434")


def get_postgres_db(knowledge_table: str | None = None) -> PostgresDb:
    """Create a PostgresDb instance.

    Args:
        knowledge_table: Optional table name for storing knowledge contents.

    Returns:
        Configured PostgresDb instance.
    """
    if knowledge_table is not None:
        return PostgresDb(id=DB_ID, db_url=db_url, knowledge_table=knowledge_table)
    return PostgresDb(id=DB_ID, db_url=db_url)


def create_knowledge(name: str, table_name: str) -> Knowledge:
    """Create a Knowledge instance with PgVector hybrid search.

    Uses a local Ollama embedding model (qwen3-embedding:4b) to avoid
    requiring an OpenAI API key for embeddings.

    Args:
        name: Display name for the knowledge base.
        table_name: PostgreSQL table name for vector storage.

    Returns:
        Configured Knowledge instance with hybrid search enabled.
    """
    return Knowledge(
        name=name,
        vector_db=PgVector(
            db_url=db_url,
            table_name=table_name,
            search_type=SearchType.hybrid,
            embedder=OllamaEmbedder(
                id="qwen3-embedding:4b",
                dimensions=2560,
                host=OLLAMA_HOST,
            ),
        ),
        contents_db=get_postgres_db(knowledge_table=f"{table_name}_contents"),
    )
