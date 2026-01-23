import pandas as pd
from sqlalchemy import create_engine, inspect
import psycopg2



class DatabaseInit():
    
    
    def __init__(self, database_name:str="", database_password:str="", database_port:str="", database_user:str="", database_host:str=""):

        self.database_name = database_name 
        self.database_password = database_password
        self.database_port = database_port 
        self.database_user = database_user
        self.database_host = database_host

        self.table_name = "gameplay_infos"
        
        self.engine = create_engine(f"postgresql+psycopg2://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}")


    def check_if_Database_exists(self) -> bool:
 
        ins = inspect(self.engine)
        return ins.has_table(self.database_name)
    

    
    def get_data_from_Database(self):

        
        db = pd.read_sql(f"SELECT match_id FROM {self.table_name}", self.engine)

        return db
    
    def upload_data_to_Database(self, df: pd.DataFrame):

        df.to_sql(self.table_name, self.engine, if_exists="append", index=False)
        