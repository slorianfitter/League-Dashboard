import pandas as pd
from sqlalchemy import create_engine, inspect
import psycopg2



class DatabaseInit():



    def __init__(
        self,
        database_name: str = "",
        user_password: str = "",
        database_port: str = "5432",
        user_name: str = "",
        database_host: str = "localhost",
        ):

        self.database_name = database_name
        self.database_port = database_port
        self.database_host = database_host
        self.user_name = user_name
        self.user_password = user_password
        

        

        # engine for the given db 

        self.engine = create_engine(f"postgresql+psycopg2://{self.user_name}:{self.user_password}@{self.database_host}:{self.database_port}/{self.database_name}")


    def check_database_connection(self) -> bool:
        """
        Tries to connect to the database to ensure it exists.
        """
        try:
            with self.engine.connect():
                print("Database connection successful!\n\n\n")
                return True

        except Exception:
            print(f"Could not connect to database. Check if everything is typed in correctly!")
            return False

    # currently useless due to the fact we will create one if there is none when data is uploaded
    def check_if_table_exists(self,table_name:str="") -> bool:

        """
        Checks if the configured table exists in the database.
        """

        inspector = inspect(self.engine)

        if inspector.has_table(table_name):
            print("Database and table found!")
            return True
        else:
            print(f"Table '{table_name}' or database '{self.database_name}' with given information not found.")
            return False

     
    def get_data_from_database(self, table_name:str="") -> pd.DataFrame:
        return pd.read_sql_table(
            table_name,
            self.engine,
            columns=["match_id"]
        )

    def upload_data_to_database(self, df: pd.DataFrame, table_name):
        '''
        Uploads the data to the given table in the initzialized database. If the table does not exist, it will creat one
        '''

        df.to_sql(table_name, self.engine, if_exists="replace", index=False)
        