from functions.helper_functions import RiotAPIClient
from functions.Database_connection import DatabaseInit
import pandas as pd
import asyncio
import time


async def main():

    #Initialisieren und starten eines Countdowns für den Api-Key. Dieser resetet sich alle 24 Stunden

    Database = DatabaseInit(database_name="league", database_password="", database_host="localhost", database_port="5432", database_user="postgres")
    client = RiotAPIClient(riot_username="", riot_password="",  ingame_name="", ingame_tag_without_hashtag="") 


    # Api Key holen.Check if api key ist eine Helper Function.

    await client.check_if_api_key_exists()


    # Eigene PUUID für den User holen -> also der der den API CLient nutzt. Damit der Spieler später seine SPiele auch richtig identifizieren kann. 
    puuid = client.get_puuid()  
    print(f"Eigene PUUID: {puuid}")


    # Gespielte Spiele -> werden als IDs gespeichert
    match_ids = client.get_match_id(puuid= puuid, count=20)
    match_ids = pd.Series(match_ids, name="match_id")
    
    print(f"Gefundene MatchIds: {len(match_ids)}")
    print(f"{match_ids}")

    # SpieleIds die bereits in der Datenbank enthalten sind

    check_database_exists = Database.check_if_Database_exists()
    if check_database_exists:
        old_match_ids = Database.get_data_from_Database()

        # Filtern der Spiele. -> Nur neue Spiele sollen abgefragt werden und dann in die Datenbank aufgenommen werden
        match_ids = match_ids[~match_ids.isin(old_match_ids["match_id"])]





    # Für jedes dieser Spiele Bitte einmal alle wichtigen Daten abrufen und direkt der Datenbank hinzufügen

    for match_id in match_ids:

        match_data = client.get_match_data(match_id)
        print(f"Stats für das Match: {match_id} gefunden")

        all_stats = client.get_match_stats(match_data)
        print(f"Spieler Stats für das Match:{match_id} gefunden")
    
        puuids = all_stats["puuid"]
        ranks = client.get_player_rank(puuid_col=puuids)
        print(f"Ranks für das Match: {match_id} gefunden")
        
        full_df = pd.merge(all_stats, ranks, on="puuid", how="left") 
        print(f"Dataframe für Match: {match_id} fertig gestellt!")
        print(full_df.head())

        Database.upload_data_to_Database(full_df)
        print("Daten erfolgreich in die Datenbank geladen")

        await asyncio.sleep(10)



if __name__ =="__main__":
    asyncio.run(main())
        

