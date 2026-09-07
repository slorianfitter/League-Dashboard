from functions.api_key.get_key import RiotAPI_KEYClient
from functions.database.Database_connection import DatabaseInit
from functions.match_data.API_Client import RiotAPIClient
import asyncio
import pandas as pd

async def main():
    # Initialize Database conncetion and check whether there is a database and the names table. Creates the respective one if not there.

    db = DatabaseInit(database_name="league", user_password="1234", user_name="postgres", database_host="localhost",database_port="5432")

    
    db_connection = db.check_database_connection()

    if db_connection: # if and only if we find the correct specified database we then proceed 


        # Initialize API-Key-Client and get api key to retrieve match data

        API_KEY_Client = RiotAPI_KEYClient(riot_username="", riot_password="Tast!")
        if not API_KEY_Client.check:
            await API_KEY_Client.get_api_key()


        # Initialize API Client to get all the wanted information
        api = RiotAPIClient(API_KEY_Client, ingame_name="MIKE%20OXMAUL", ingame_tag="FEED")

        #1. get the users puuid. very important to get match data

        api.get_puuid() # now the client knows the puuid of the user

        # We retrieve all the match_ids. Riot will allow 100 per batch so we use this batch. For the sake of just getting the data we simply do not care if errors will happen if there are no match data stored anymore 
        for i in [0,100,200,300,400,500,600,700,800]:
            match_ids = pd.Series(api.get_match_id(start=i, count=100))
            pd.DataFrame(match_ids).to_csv("D:/Projekte/league_dashboard/match_ids.csv")

            # if the table for the match data exists perfect, if not skip. Select only data that is not in DB.

            check_if_tables_exist = db.check_if_table_exists("start_end_game")

            if check_if_tables_exist:
                match_ids_in_db = db.get_data_from_database("start_end_game")
                match_ids = match_ids[~match_ids.isin(match_ids_in_db["match_id"])]

            for match_id in match_ids:

                data = api.get_match_data(match_id) # huge list of match data
                match_stats = api.get_match_stats(data) # list with filterer match data -> match stats 

                db.upload_data_to_database(match_stats, "match_data_end")
                print(f"match_stats for matchId = {match_id} uploaded!")

                del data

                await asyncio.sleep(1)

                # delete so we don't run out of ram

                player_ranks = api.get_player_rank(match_stats["puuid"]) # list of player ranks with several stats such as winrate etc -> list
                player_ranks["match_id"] = match_id
                db.upload_data_to_database(player_ranks, "user_ranks")
                print(f"player ranks for matchId = {match_id} uploaded!")

                del player_ranks
                del match_stats

                await asyncio.sleep(1)
                match_data_timeline = api.get_match_data_timeline(matchId=match_id)

                df_event_timeline = api.get_match_stats_timeline(match_data_timeline)
                del match_data_timeline

                db.upload_data_to_database(df_event_timeline["start_end_game"], "start_end_game")
                db.upload_data_to_database(df_event_timeline["event_timeline"], "event_timeline")
                db.upload_data_to_database(df_event_timeline["assists"], "assists")
                db.upload_data_to_database(df_event_timeline["kills"], "kills")
                db.upload_data_to_database(df_event_timeline["monster_kills"], "monster_kills")
                db.upload_data_to_database(df_event_timeline["turret_kills"], "turret_kills")
                db.upload_data_to_database(df_event_timeline["bounty"], "bounty")
                db.upload_data_to_database(df_event_timeline["skill_level"], "skill_level")
                db.upload_data_to_database(df_event_timeline["item_history"], "item_history")
                db.upload_data_to_database(df_event_timeline["ward_history"], "ward_history")
                db.upload_data_to_database(df_event_timeline["participant_stats"], "participant_stats")

                del df_event_timeline
                # upload data. if the tables dont exist it will creat one and upload the data immediately.


                print(f"matchId = {match_id} finished!\n\n-------------------------------------------------------------------\n")
                await asyncio.sleep(3)
                # make sure we delete the objects after each iteration to ensure we always have enough RAM! Of course python does this automatically but this is another ensurance that there is enough ram!


            
            

if __name__ == "__main__":
    asyncio.run(main())


