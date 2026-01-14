from sqlalchemy import Table, MetaData, insert
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from dotenv import load_dotenv
from datetime import time
import pandas as pd


def get_engine(echo: bool = False):
    import os
    from dotenv import load_dotenv

    load_dotenv()

    user = os.getenv("user")
    password = os.getenv("password")
    host = os.getenv("host")
    port = os.getenv("port")
    dbname = os.getenv("dbname")

    database_url = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{dbname}?sslmode=require"

    return create_engine(
        database_url,
        echo=True,
        pool_size=10,          # increase max connections
        max_overflow=5,        # allow temporary extra connections
        pool_timeout=60,       # wait 30s for connection before error
    )


def insert_dataframe(df: pd.DataFrame, table_name: str, engine, schema="public", chunk_size=250, conflict_cols=None):
    """
    Insert a DataFrame into PostgreSQL safely with duplicates ignored and proper transaction handling.

    Parameters:
    - df: pandas DataFrame to insert
    - table_name: target table in PostgreSQL
    - engine: SQLAlchemy engine
    - schema: PostgreSQL schema (default 'public')
    - chunk_size: number of rows per insert chunk
    - conflict_cols: list of columns to use for ON CONFLICT (must be UNIQUE or PK)
    """

    if df.empty:
        return

    # 1️⃣ Clean column names (remove _m0, _m1, etc.)
    df.columns = [col.split('_m')[0] for col in df.columns]

    # 2️⃣ Cast nullable integer columns to Int64
    nullable_int_cols = ['numero_ordre', 'vent_direction', 'vent_force', 'mer_force']
    for col in nullable_int_cols:
        if col in df.columns:
            df[col] = df[col].astype('Int64')  # allows None/NaN -> NULL

    # 3️⃣ Ensure operation_id is BIGINT
    if 'operation_id' in df.columns:
        df['operation_id'] = df['operation_id'].astype('int64')

    # 4️⃣ Reflect table metadata
    meta = MetaData()
    tbl = Table(table_name, meta, autoload_with=engine, schema=schema)

    # 5️⃣ Insert in chunks
    for start in range(0, len(df), chunk_size):
        chunk = df.iloc[start:start + chunk_size]
        records = chunk.to_dict(orient="records")

        with engine.connect() as conn:
            try:
                with conn.begin():  # transaction-safe
                    for row in records:
                        stmt = insert(tbl).values(**row)
                        if conflict_cols:
                            stmt = stmt.on_conflict_do_nothing(index_elements=conflict_cols)
                        conn.execute(stmt)
            except Exception as e:
                conn.rollback()
                raise e

    # 6️⃣ Dispose engine at the very end (optional)
    # engine.dispose()