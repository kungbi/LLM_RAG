import pandas as pd
import os
import sys
from sqlalchemy import create_engine
from utils.db_api import DB_Configuration


def get_engine(db_info: DB_Configuration):
    connection_string = f"mssql+pyodbc://{db_info.username}:{db_info.password}@{db_info.hostname}:{db_info.port}/{db_info.database_name}?driver={db_info.driver}&TrustServerCertificate=yes"
    return create_engine(connection_string)


def execute_query(engine, query):
    try:
        df = pd.read_sql(query, engine)
        for col in df.columns:
            if df[col].dtype == "object" and isinstance(df[col].iloc[0], bytes):
                df[col] = df[col].apply(lambda x: int.from_bytes(x, "big"))
        return df
    except Exception as ex:
        print("Error: ", ex)
        return None


# 테이블 정보 쿼리
table_info_query = """
SELECT 
    TABLE_SCHEMA,
    TABLE_NAME
FROM 
    INFORMATION_SCHEMA.TABLES
WHERE 
    TABLE_TYPE = 'BASE TABLE';
"""

# 컬럼 정보 쿼리
column_info_query = """
SELECT 
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM 
    INFORMATION_SCHEMA.COLUMNS
ORDER BY 
    TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION;
"""

# 참조 관계 정보 쿼리
foreign_key_info_query = """
SELECT 
    fk.name AS FK_Name,
    tp.name AS Parent_Table,
    tr.name AS Referenced_Table,
    c.name AS Column_Name,
    cr.name AS Referenced_Column_Name
FROM 
    sys.foreign_keys AS fk
INNER JOIN 
    sys.tables AS tp ON fk.parent_object_id = tp.object_id
INNER JOIN 
    sys.tables AS tr ON fk.referenced_object_id = tr.object_id
INNER JOIN 
    sys.foreign_key_columns AS fkc ON fk.object_id = fkc.constraint_object_id
INNER JOIN 
    sys.columns AS c ON fkc.parent_column_id = c.column_id AND fkc.parent_object_id = c.object_id
INNER JOIN 
    sys.columns AS cr ON fkc.referenced_column_id = cr.column_id AND fkc.referenced_object_id = cr.object_id
ORDER BY 
    tp.name, c.name;
"""

# 데이터 10개씩 추출 쿼리 템플릿
select_data_query = """
SELECT TOP 10 *
FROM {schema}.{table}
ORDER BY newid()
"""

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)


def table_info_to_string(table_name, info):
    columns_str = "\n".join(
        [
            f"{col['COLUMN_NAME']} (type: {col['DATA_TYPE']}, length: {col['CHARACTER_MAXIMUM_LENGTH']}, nullable: {col['IS_NULLABLE']}, default: {col['COLUMN_DEFAULT']})"
            for col in info["columns"]
        ]
    )

    foreign_keys_str = "\n".join(
        [
            f"{fk['FK_Name']}: {fk['Column_Name']} -> {fk['Referenced_Table']}.{fk['Referenced_Column_Name']}"
            for fk in info["foreign_keys"]
        ]
    )

    data_str = "\n".join([str(row) for row in info["data"]])

    table_str = f"""
======= {table_name} table =======

======= Columns =======
{columns_str}

======= Foreign Keys =======
{foreign_keys_str}

======= Data (10 random rows) =======
{data_str}
"""
    return table_str


def start(db_info: DB_Configuration):
    engine = get_engine(db_info)

    table_info_df = execute_query(engine, table_info_query)
    column_info_df = execute_query(engine, column_info_query)
    foreign_key_info_df = execute_query(engine, foreign_key_info_query)

    database_info = {}

    if table_info_df is not None:
        for schema, table in zip(
            table_info_df["TABLE_SCHEMA"], table_info_df["TABLE_NAME"]
        ):
            table_key = f"{schema}.{table}"
            database_info[table_key] = {}

            column_info = column_info_df[column_info_df["TABLE_NAME"] == table]
            database_info[table_key]["columns"] = column_info.to_dict(orient="records")

            foreign_key_info = foreign_key_info_df[
                foreign_key_info_df["Parent_Table"] == table
            ]
            database_info[table_key]["foreign_keys"] = foreign_key_info.to_dict(
                orient="records"
            )

            query = select_data_query.format(schema=schema, table=table)
            try:
                data_df = execute_query(engine, query)
                if data_df is not None:
                    database_info[table_key]["data"] = data_df.to_dict(orient="records")
                else:
                    database_info[table_key]["data"] = []
            except Exception as e:
                print(f"Could not retrieve data from table {schema}.{table}: {e}")
                database_info[table_key]["data"] = []

    for table, info in database_info.items():
        table_str = table_info_to_string(table, info)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "../../schema")
        path = os.path.join(output_dir, f"{table}.txt")

        with open(path, "w") as file:
            file.write(table_str)
