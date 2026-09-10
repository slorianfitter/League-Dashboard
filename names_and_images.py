from functions.images import dashboard_images
from functions.database import Database_connection
import pandas as pd


# start with the database

db = Database_connection.DatabaseInit(database_name="league", user_password="1234", user_name="postgres", database_host="localhost",database_port="5432")

# check if there is a connection

if db.check_database_connection():
    dash = dashboard_images.Dashboard_Images()

    db.upload_data_to_database(pd.DataFrame(dash.Champion()), table_name="Champions")
    db.upload_data_to_database(pd.DataFrame(dash.Item()), table_name="Items")
    db.upload_data_to_database(pd.DataFrame(data= dash.Rune()), table_name="Runes")

    print("\n\n ---------------------------------------\n\n Data uploaded to Tables in Database! \n\n --------------------------------------- \n\n")