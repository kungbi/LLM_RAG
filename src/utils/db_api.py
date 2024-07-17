from typing import Dict, List, Union
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
import pandas as pd


class DB_Configuration:
    def __init__(self, hostname, port, username, password, database_name, driver):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.database_name = database_name
        self.driver = driver

    def to_dict(self):
        return {
            "hostname": self.hostname,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "database_name": self.database_name,
            "driver": self.driver,
        }


class DBAPI:
    def __init__(self) -> None:
        self.configurations: Dict[int, DB_Configuration] = {}
        self.id_generator = 0

    def get_id(self):
        tmp = self.id_generator
        self.id_generator += 1
        return tmp

    def add_configuration(self, db_info: DB_Configuration):
        id = self.get_id()
        self.configurations[id] = db_info

    def get_configuration(self, id):
        return self.configurations.get(id, None)

    def get_configurations(self) -> List[Dict[int, DB_Configuration]]:
        return list(self.configurations.items())

    def delete_configuration(self, id):
        self.configurations.pop(id)

    def get_connection_url(self, db_info: DB_Configuration):
        return URL.create(
            "mssql+pyodbc",
            username=db_info.username,
            password=db_info.password,
            host=f"{db_info.hostname},{db_info.port}",
            database=db_info.database_name,
            query={"driver": db_info.driver, "TrustServerCertificate": "yes"},
        )

    def test_connection(self, id) -> Dict[str, Union[bool, Exception]]:
        db_info = self.get_configuration(id)
        connection_url = self.get_connection_url(db_info)
        try:
            engine = create_engine(connection_url)
            return {"result": True}
        except Exception as e:
            return {"result": False, "error": e}

    def execute(self, id, query):
        db_info = self.get_configuration(id)
        connection_url = self.get_connection_url(db_info)
        try:
            engine = create_engine(connection_url)
            with engine.connect() as conn:
                df = pd.read_sql(query, conn)
                return {"result": True, "sql_result": df}
        except Exception as ex:
            return {"result": False, "error": ex}


# db_info = DB_Configuration(
#     hostname="localhost",
#     username="sa",
#     password="Ithink%Th5r5f0re$Iam",
#     port=1433,
#     database_name="school",
#     driver="ODBC Driver 18 for SQL Server",
# )
# db_api = DBAPI()
# db_api.add_configuration(db_info)
# db_api.add_configuration(db_info)
# db_list = db_api.get_configurations()

# print(db_api.test_connection(0))

# df = db_api.execute(0, "SELECT * FROM PERSON;")
# print(df)
