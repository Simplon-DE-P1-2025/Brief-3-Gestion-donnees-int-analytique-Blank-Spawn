import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def get_engine(echo: bool = False) -> Engine:
    """
    Create and return a SQLAlchemy engine connected to Supabase Postgres.
    """
    load_dotenv()

    user = os.getenv("user")
    password = os.getenv("password")
    host = os.getenv("host")
    port = os.getenv("port")
    dbname = os.getenv("dbname")

    missing = [k for k, v in {
        "user": user,
        "password": password,
        "host": host,
        "port": port,
        "dbname": dbname,
    }.items() if not v]

    if missing:
        raise RuntimeError(f"Missing env variables: {', '.join(missing)}")

    database_url = (
        f"postgresql+psycopg2://{user}:{password}"
        f"@{host}:{port}/{dbname}?sslmode=require"
    )

    return create_engine(database_url, echo=echo)


import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine


def insert_dataframe(
    df: pd.DataFrame,
    table_name: str,
    engine: Engine,
    schema: str = "public",
):
    """
    Insert a pandas DataFrame into a PostgreSQL table.
    """
    if df.empty:
        return

    df.to_sql(
        name=table_name,
        con=engine,
        schema=schema,
        if_exists="append",
        index=False,
        method="multi",
    )