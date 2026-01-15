from sqlalchemy import Table, MetaData
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.dialects.postgresql import insert
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


def insert_dataframe(
    df: pd.DataFrame,
    table_name: str,
    engine,
    schema="public",
    chunk_size=250,
    conflict_cols=None,
    conflict_constraint=None,
):
    if df.empty:
        return

    # 1️⃣ Nullable integers
    nullable_int_cols = ['numero_ordre', 'vent_direction', 'vent_force', 'mer_force']
    for col in nullable_int_cols:
        if col in df.columns:
            df[col] = df[col].astype('Int64')

    # 1.5️⃣ Replace NaN in string columns with empty strings
    string_cols = df.select_dtypes(include=['object', 'string']).columns
    for col in string_cols:
        df[col] = df[col].fillna('')

    # 2️⃣ operation_id
    if 'operation_id' in df.columns:
        df['operation_id'] = df['operation_id'].astype('int64')

    # 4️⃣ Reflect table
    meta = MetaData()
    tbl = Table(table_name, meta, schema=schema, autoload_with=engine)

    # 5️⃣ Reuse ONE connection
    with engine.connect() as conn:
        for start in range(0, len(df), chunk_size):
            chunk = df.iloc[start:start + chunk_size]
            records = chunk.to_dict(orient="records")

            stmt = insert(tbl).values(records)

            if conflict_constraint:
                stmt = stmt.on_conflict_do_nothing(
                    constraint=conflict_constraint
                )
            elif conflict_cols:
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=conflict_cols
                )

            # One transaction per chunk
            with conn.begin():
                conn.execute(stmt)