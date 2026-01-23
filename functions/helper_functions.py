import pandas as pd
import requests
import asyncio
from pydoll.browser.chromium import Chrome
from pydoll.browser.options import ChromiumOptions
from pydoll.constants import Scripts
from urllib.parse import quote, unquote
import os


from datetime import datetime, timedelta



class RiotAPIClient:
        
    def __init__(self, riot_username:str="", riot_password:str="", ingame_name:str="", ingame_tag_without_hashtag:str=""):
        self.riot_username = riot_username
        self.riot_password = riot_password

        self.ingame_name = quote(ingame_name)
        self.ingame_tag_without_hashtag = f"/{quote(ingame_tag_without_hashtag)}"

        self.api_key_file = "D:/Projekte/selbststudium/Python/API/api_key_riot_games.csv"

        self.check = False

        if os.path.exists(self.api_key_file):
            try:
                self.api_file = pd.read_csv(self.api_key_file)
                self.api_key = self.api_file["api_key"].iloc[0]
                self.api_key_time = pd.to_datetime(self.api_file["time"].iloc[0], errors="coerce")
                self.check = True
            except ValueError:
                print("Datei kann nicht geladen werden oder es gibt ein Problem mit den dtypes")


        
        self.base_url_europe = "https://europe.api.riotgames.com"
        self.base_url_euw = "https://euw1.api.riotgames.com"



    async def check_if_api_key_exists(self):
            if not self.check:
                print("Kein Key vorhanden / keine Datei vorhanden")
                await self.get_api_key()
            
            else:
                current_time = datetime.now()
                time_from_key= self.api_key_time

                if current_time - time_from_key > timedelta(hours=24):
                    print("Key abgelaufen - Beschaffe neuen Key")
                    await self.get_api_key()
                else:
                    print("Key ist noch gültig")
                    

    async def get_api_key(self):

        options = ChromiumOptions()
        options.headless = False
        async with Chrome(options = options) as browser:
            tab = await browser.start()
            await tab.go_to('https://developer.riotgames.com/apis')


            await asyncio.sleep(5)
            
            button = await tab.find(class_name='navbar-avatar')
            
            if button:
                print("Button gefunden! Klicke jetzt...")
                await button.click() 
                await asyncio.sleep(2)  # Warte nach dem Klick
                await tab.get_cookies()
                await asyncio.sleep(2)

                # Suche die Felder auf der TAB-Ebene, nicht unter button
                
                benutzername = await tab.find(data_testid="input-username")
                password = await tab.find(data_testid = "input-password")

                if benutzername and password:
                    await benutzername.type_text(self.riot_username, humanize=True)

                    await asyncio.sleep(2)
                    await password.type_text(self.riot_password, humanize=True)
                    await asyncio.sleep(2)


                    login_btn = await tab.find(data_testid = "btn-signin-submit")
                    await asyncio.sleep(5)
                    if login_btn:
                        await login_btn.click()
                        await asyncio.sleep(10)

                    else:
                        print("Login-Button konnte nicht gefunden werden.")
                        return None
                    
                    drop_down_bar = await tab.find(class_name = 'admin-title')

                    if drop_down_bar:                 
                        await drop_down_bar.click()
                        await asyncio.sleep(2)

                        dashboard = await tab.find(text='Dashboard')
                        if dashboard:
                            await dashboard.click()

                            await asyncio.sleep(10)
                        else:
                            print("Dashboard konnte nicht gefunden werden")
                            return None
                        
                    
                        await tab.execute_script("document.body.style.zoom = '0.5'")
                        await asyncio.sleep(5)

                        re_iframe = await tab.find(title="reCAPTCHA")
                        
                        if re_iframe:
                            print("IFrame gefunden!")
                            await re_iframe.click()
                        else:
                            return None


                        await  asyncio.sleep(10)
                        submit = await tab.find(type='submit')

                        if submit:
                            await submit.click()
                            await asyncio.sleep(4)
                        else:
                            print("submit button konnte nicht gefunden werden")
                            return None
                        
                        await asyncio.sleep(10)
                        api_key = await tab.find(id='apikey')
                        
                        
                        if api_key:
                            print("api-key konnte gefunden werden")

                            self.api_key = api_key.get_attribute("value")
                            self.api_key_time = datetime.now()
                            df_api =  pd.DataFrame({"api_key": self.api_key
                                                    ,"time": [self.api_key_time]})
                            self.check = True
                            
                            return df_api.to_csv(self.api_key_file, index=False)
                        
                        else:
                            return None
                    else:
                        print("Dropdownbar nicht genfunden")


                else:
                    print("Benutzername- oder Passwort-Feld konnte nicht gefunden werden.")
            else:
                print("Button konnte nicht gefunden werden.")

        return None
        


    def get_puuid(self):
        
        api_link ="/riot/account/v1/accounts/by-riot-id/"

        full_link = f"{self.base_url_europe}{api_link}{str(self.ingame_name)}{str(self.ingame_tag_without_hashtag)}?api_key={str(self.api_key)}"
        res = requests.get(full_link).json()
        puuid = res["puuid"]


        return puuid



    def get_match_id(self, puuid: str, start: int=0, count: int=20) -> list:
        api_link = f"/lol/match/v5/matches/by-puuid/{puuid}/ids"
        full_link = f"{self.base_url_europe}{api_link}?start={start}&count={count}&api_key={self.api_key}"
        
        
        
        res4 = requests.get(full_link).json()

        list_of_match_ids = [x for x in res4]
        

        return list_of_match_ids



    def get_match_data(self, matchId: str)-> dict: 


        api_link =f"/lol/match/v5/matches/{matchId}"


        full_link = f"{self.base_url_europe}{api_link}?api_key={self.api_key}"
        res = requests.get(full_link).json()

        return res


    def get_match_stats(self, res):

        player_stats =  []

        for i in range(0,10):

            player_info = res["info"]["participants"][i]
            
            stats_dict = {

                #meta_data 
            

                            "match_id": str(res["metadata"]["matchId"]),
                            "date": pd.to_datetime(res["info"]["gameCreation"], unit="ms", errors="coerce"),
                            "game_duration_in_seconds": int(res["info"]["gameDuration"]),

                

                # Player information
                            "puuid": player_info["puuid"],
                            "riotId_name": player_info["riotIdGameName"],
                            "riotId_tag": player_info["riotIdTagline"],
                            

                # Champ played

                            "champ": player_info["championName"],
                            "champ_id": player_info["championId"],


                # Lane  
                            "lane": player_info["individualPosition"],


                #Stats

                            "kills": player_info["kills"],
                            "deaths": player_info["deaths"],
                            "assists": player_info["assists"],
                            "total_damage_dealt": player_info["totalDamageDealt"],
                            "vision_score": player_info["visionScore"],
                            "wards_placed": player_info["wardsPlaced"],


                # Gold
                            "gold": player_info["goldEarned"],


                # CS
                            "first_10_min_cs": int(player_info["challenges"]["laneMinionsFirst10Minutes"] + player_info["challenges"]["jungleCsBefore10Minutes"]),
                            "total_cs": player_info["totalMinionsKilled"],
                            "jgl_camps": (int(player_info["totalAllyJungleMinionsKilled"]) + int(player_info["totalEnemyJungleMinionsKilled"])),


                # Objectives

                            "turrets_killed": player_info["turretKills"],
                            "turret_takedowns": player_info["turretTakedowns"],
                            "building_damage": player_info["damageDealtToBuildings"],
                            "epic_monster_damage": player_info["damageDealtToEpicMonsters"],


                # Items
                            "item_0": int(player_info["item0"]),
                            "item_1": int(player_info["item1"]),
                            "item_2": int(player_info["item2"]),
                            "item_3": int(player_info["item3"]),
                            "item_4": int(player_info["item4"]),
                            "item_5": int(player_info["item5"]),
                            "vision_item": int(player_info["item6"]),


                # Perks
                            # main tree:
                            "key_runes": [x["perk"] for x in player_info["perks"]["styles"][0]["selections"]],

                            # sub tree
                            "sub_runes": [x["perk"] for x in player_info["perks"]["styles"][1]["selections"]],

                            # flatstats
                            "stat_rune_def": int(player_info["perks"]["statPerks"]["defense"]),
                            "stat_rune_flex": int(player_info["perks"]["statPerks"]["flex"]),
                            "stat_rune_of": int(player_info["perks"]["statPerks"]["offense"]),
        

                #type of kills:
                            "double":   int(player_info["doubleKills"]),
                            "triple":   int(player_info["tripleKills"]),
                            "quadra":   int(player_info["quadraKills"]),
                            "penta":    int(player_info["pentaKills"]),

                # win?
                            "win": player_info["win"]
            }

            player_stats.append(stats_dict)

        return pd.DataFrame(player_stats)



        
    def get_player_rank(self, puuid_col: pd.Series):


        list_of_ranks_per_puuid = []

        api_link = "/lol/league/v4/entries/by-puuid/"

        for puuid in puuid_col:

            full_link = f"{self.base_url_euw}{api_link}{puuid}?api_key={self.api_key}"
            res = requests.get(full_link).json() 


            if isinstance(res, list) and len(res) > 0:

                for entry in res:
                    if entry.get("queueType") == "RANKED_SOLO_5x5":
                        solo_entry = entry
                        list_of_ranks_per_puuid.append(solo_entry)
            else: 
                # Liste war leer [] -> Spieler hat gar keinen Rang
                list_of_ranks_per_puuid.append(
                    {
                    "leagueId": None,
                    "queueType": "RANKED_SOLO_5x5",
                    "tier": None, 
                    "rank": None, 
                    "puuid": puuid,
                    "leaguePoints": None, 
                    "wins": None, 
                    "losses": None,
                    "veteran": False,
                    "inactive": False,
                    "freshBlood": None,
                    "hotstreak": False
                }
                )

        return print(pd.DataFrame(list_of_ranks_per_puuid))

