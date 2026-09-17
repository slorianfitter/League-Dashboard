import pandas as pd
import requests

from functions.api_key.get_key import RiotAPI_KEYClient


class RiotAPIClient:

    
    def __init__(self, key_client, ingame_name:str="", ingame_tag:str=""):

        self.key_client = key_client
        self.base_url_europe = "https://europe.api.riotgames.com"
        self.base_url_euw = "https://euw1.api.riotgames.com"

        self.ingame_name = ingame_name
        self.ingame_tag = ingame_tag

        
        riot = RiotAPI_KEYClient()
        if not riot.check:
            riot.get_api_key()

        self.key_client = RiotAPI_KEYClient()

        if not self.key_client.check:
            self.key_client.get_api_key()

        self.api_key = self.key_client.api_key
        self.puuid = None


    def get_puuid(self):
        
        api_link ="/riot/account/v1/accounts/by-riot-id/"

        full_link = f"{self.base_url_europe}{api_link}{self.ingame_name}/{self.ingame_tag}?api_key={self.api_key}"

        res = requests.get(full_link).json()

        self.puuid = res["puuid"]


        
    def get_match_id(self, start: int=0, count: int=100) -> list:

        api_link = f"/lol/match/v5/matches/by-puuid/{self.puuid}/ids"
        full_link = f"{self.base_url_europe}{api_link}?type=ranked&start={start}&count={count}&api_key={self.api_key}"


        res4 = requests.get(full_link).json()
        list_of_match_ids = [x for x in res4]
        

        return list_of_match_ids



    def get_match_data(self, matchId: str)-> dict: 


        api_link =f"/lol/match/v5/matches/{matchId}"

        
        full_link = f"{self.base_url_europe}{api_link}?api_key={self.api_key}"

        data = requests.get(full_link).json()
        return data



    def get_match_stats(self, data:dict) -> pd.DataFrame:

        if data["info"]["endOfGameResult"] != "GameComplete":
            return None
        player_stats =  []
        
        for i in range(0,10):

            
            player_info =   data["info"]["participants"][i]
            
            stats_dict = {

                #meta_data 
            

                            "match_id": str(data["metadata"]["matchId"]),
                            "date": pd.to_datetime(data["info"]["gameCreation"], unit="ms", errors="coerce"),
                            "game_duration_in_seconds": int(data["info"]["gameDuration"]),

                

                # Player information
                            "puuid": player_info["puuid"],
                            "riotId_name": player_info["riotIdGameName"],
                            "riotId_tag": player_info["riotIdTagline"],
                            "participantId": i+1,
                            

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



    def get_match_data_timeline(self, matchId: str)-> dict: 


        api_link =f"/lol/match/v5/matches/{matchId}/timeline"
        
        
        full_link = f"{self.base_url_europe}{api_link}?api_key={self.api_key}"
        data_timeline = requests.get(full_link).json()

        return data_timeline



    def get_match_stats_timeline(self, data: dict) -> dict:

        if data["info"]["endOfGameResult"] != "GameComplete":
            return None

        match_id = str(data["metadata"].get("matchId")) ### primary key in database!!!  
    
        event_timeline_rows = []

        kills_rows = []
        assist_rows = []
        monster_kills_rows = []
        turret_kills_rows = []
        bounty_rows = []
        skill_level_rows = []
        item_history_rows = []
        wards_history_rows = []

        participant_champ_stats_rows = []
        participant_damage_stats_rows = []
        participant_other_stats_rows = []

        start_end_game_rows = []

        i = 0
        for frame in data["info"]["frames"]:
            for event in frame["events"]:

                i+=1 # unique event counter 

                event_type = event.get("type") #unique per game


                event_dict = {"match_id":   match_id,"event_number":    i, "event_type":    event_type, "timestamp":    event.get("timestamp")}
                event_timeline_rows.append(event_dict) ##

                #start/end game
                if event_type == "PAUSE_END":  
                    start_end_game_rows.append({
                        "match_id":  match_id,
                        "event_number": i,
                        "event_type":    event_type,
                        "realTimestamp":    event.get("realTimestamp"),
                        "timestamp":    event.get("timestamp")
                        })


                elif event_type == "GAME_END":
                    start_end_game_rows.append({
                        "match_id":  match_id,
                        "event_number": i,
                        "event_type":    event_type,
                        "realTimestamp":    event.get("realTimestamp"),
                        "timestamp":    event.get("timestamp"),
                        "winningTeam":  event.get("winningTeam")
                        })


                #items
                elif event_type == "ITEM_PURCHASED":

                    item_history_rows.append({
                        "match_id":  match_id,
                        "event_number": i,
                        "event_type":   event.get("type"),
                        "itemId":   event.get("itemId"),
                        "participantId":    event.get("participantId"),
                        "timestamp":    event.get("timestamp"),
                        })

                elif event_type == "ITEM_DESTROYED":
                    item_history_rows.append({
                        "match_id":  match_id,
                        "event_number": i,
                        "event_type":   event.get("type"),
                        "itemId":   event.get("itemId"),
                        "participantId":    event.get("participantId"),
                        "timestamp":    event.get("timestamp")
                        })

                elif event_type == "ITEM_SOLD":
                    item_history_rows.append({
                        "match_id":  match_id,
                        "event_number": i,
                        "event_type":   event.get("type"),
                        "itemId":  event.get("itemId"),
                        "participantId":    event.get("participantId"),
                        "timestamp":   event.get("timestamp")
                        })

                elif event_type == "ITEM_UNDO":
                    item_history_rows.append({
                        "match_id":  match_id,                  
                        "event_number": i,
                        "event_type":   event.get("type"),
                        "participantId" :   event.get("participantId"),
                        "timestamp" :   event.get("timestamp"),
                        "afterId":  event.get("afterId"),
                        "beforeId" :    event.get("beforeId"),
                        "goldGain" :    event.get("goldGain")
                        })

                #level/skills
                elif event_type == "LEVEL_UP":
                    skill_level_rows.append({
                        "match_id":  match_id,                  
                        "event_number": i,
                        "event_type":   event.get("type"),
                        "level":   event.get("level"),
                        "participantId":    event.get("participantId"),
                        "timestamp":    event.get("timestamp")
                        })


                elif event_type == "SKILL_LEVEL_UP":
                    skill_level_rows.append({
                        "match_id":  match_id,
                        "event_number": i,
                        "event_type":   event.get("type"),
                        "skillSlot": event.get("skillSlot"),
                        "participantId":    event.get("participantId"),
                        "timestamp":    event.get("timestamp")
                        })
                    

                #wards
                elif event_type == "WARD_PLACED":
                    wards_history_rows.append({
                    "match_id":  match_id,
                    "event_number": i,
                    "event_type":   event.get("type"),
                    "event_number": i,
                    "creatorId":    event.get("creatorId"),
                    "timestamp":    event.get("timestamp"),
                    "wardType": event.get("wardType")
                    })

                elif event_type == "WARD_KILL":
                    wards_history_rows.append({
                    "match_id":  match_id,
                    "event_number": i,
                    "event_type":   event.get("type"),
                    "killerId": event.get("killerId"),
                    "timestamp":    event.get("timestamp"),
                    "wardType": event.get("wardType")
                    })



                elif event_type == "CHAMPION_KILL":
                    position = event.get("position")

                    kills_rows.append({
                    "match_id":  match_id,
                    "event_number": i,
                    "event_type":   event_type,
                    "victimId": event.get("victimId"),
                    "killType": event.get("killType"),
                    "killerId": event.get("killerId"),
                    "timestamp" :   event.get("timestamp"),
                    "position_x":   position.get("x"),
                    "position_y":   position.get("y"),
                    })

                    # the damage the victim received # stored in a sperate table

                    damage_received = event.get("victimDamageReceived")

                    for damage in damage_received:
                        assist_rows.append({
                            "match_id": match_id,  # primary key 1:1
                            "event_number": i,
                            "timestamp": event.get("timestamp"),
                            "basic": damage.get("basic"),
                            "magicDamage": damage.get("magicDamage"),
                            "name": damage.get("name"),
                            "participantId": damage.get("participantId"),  # important to reconstruct KDA 
                            "physicalDamage": damage.get("physicalDamage"),
                            "spellName": damage.get("spellName"),
                            "spellSlot": damage.get("spellSlot"),
                            "trueDamage": damage.get("trueDamage"),
                            "damageType": damage.get("type"),
                            "victimId": event.get("victimId"),
                            "is_killer": damage.get("participantId") == event.get("killerId")
                        })

                elif event_type == "CHAMPION_SPECIAL_KILL":
                    position = event.get("position")
                    kills_rows.append({
                        "match_id": match_id, 
                        "event_number": i,
                        "event_type":    event_type,
                        "killType": event.get("killType"),
                        "killerId":    event.get("killerId"),
                        "multiKillLength":  event.get("multiKillLength"),
                        "timestamp":    event.get("timestamp"),
                        "position_x" : position.get("x"),
                        "position_y" : position.get("y")
                        })



                elif event_type == "TURRET_PLATE_DESTROYED":
                    position = event.get("position")
                    turret_kills_rows.append({
                        "match_id": match_id, 
                        "event_number": i,
                        "event_type":    event_type,
                        "killerId": event.get("killerId"),
                        "laneType": event.get("laneType"),
                        "teamId":   event.get("teamId"),
                        "timestamp":    event.get("timestamp"),
                        "position_x":   position.get("x"),
                        "position_y":   position.get("y"),
                        })
                elif event_type == "BUILDING_KILL":
                    position = event.get("position")
                    turret_kills_rows.append({
                        "match_id": match_id, 
                        "event_number": i,
                        "event_type":    event_type,
                        "bounty":   event.get("bounty"),
                        "buildingType": event.get("buildingType"),
                        "killerId": event.get("killerId"),
                        "laneType": event.get("laneType"),
                        "teamId":  event.get("teamId"),
                        "timestamp":    event.get("timestamp"),
                        "towerType":    event.get("towerType"),
                        "position_x":   position.get("x"),
                        "position_y":   position.get("y")
                        })
                elif event_type == "OBJECTIVE_BOUNTY_FINISH":
                    bounty_rows.append({
                        "match_id": match_id, 
                        "event_number": i,
                        "event_type":    event_type,
                        "teamId":   event.get("teamId"),
                        "timestamp":    event.get("timestamp")
                        })
                elif event_type == "OBJECTIVE_BOUNTY_PRESTART":
                    bounty_rows.append({
                        "match_id": match_id, 
                        "event_number": i,
                        "event_type":    event_type,
                        "teamId":   event.get("teamId"),
                        "timestamp":    event.get("timestamp")
                        })

                elif event_type == "ELITE_MONSTER_KILL":
                    position=  event.get("position")
                    monster_kills_rows.append({
                        "match_id": match_id, 
                        "event_number": i,
                        "event_type":    event_type,
                        "bounty" : event.get("bounty"),  # bounty usually happens when one time is far behind. will only be granted to the team that is behind
                        "killerId" : event.get("killerId"),
                        "killerTeamId" : event.get("killerTeamId"),  # Which team hit the last
                        "monsterSubType" : event.get("monsterSubType"),
                        "monsterType" : event.get("monsterType"),
                        "timestamp" : event.get("timestamp"),
                        "position_x": position.get("x"),
                        "position_y" : position.get("y"),
                        })

                else:
                    # unknown event type 
                    continue


            for participant in frame["participantFrames"].values():
                champion_stats = participant.get("championStats") 
                damage_stats = participant.get("damageStats") 
                position = participant.get("position")

                participant_champ_dict = {
                    "match_id": match_id,
                    "event_number": i,
                    "participantId": participant.get("participantId"),
                    "timestamp": frame.get("timestamp"),
                    "abilityHaste": champion_stats.get("abilityHaste"),
                    "abilityPower": champion_stats.get("abilityPower"),
                    "armor": champion_stats.get("armor"),
                    "armorPen": champion_stats.get("armorPen"),
                    "armorPenPercent": champion_stats.get("armorPenPercent"),
                    "attackDamage": champion_stats.get("attackDamage"),
                    "attackSpeed": champion_stats.get("attackSpeed"),
                    "bonusArmorPenPercent": champion_stats.get("bonusArmorPenPercent"),
                    "bonusMagicPenPercent": champion_stats.get("bonusMagicPenPercent"),
                    "ccReduction": champion_stats.get("ccReduction"),
                    "cooldownReduction": champion_stats.get("cooldownReduction"),
                    "health": champion_stats.get("health"),
                    "healthMax": champion_stats.get("healthMax"),
                    "healthRegen": champion_stats.get("healthRegen"),
                    "lifesteal": champion_stats.get("lifesteal"),
                    "magicPen": champion_stats.get("magicPen"),
                    "magicPenPercent": champion_stats.get("magicPenPercent"),
                    "magicResist": champion_stats.get("magicResist"),
                    "movementSpeed": champion_stats.get("movementSpeed"),
                    "omnivamp": champion_stats.get("omnivamp"),
                    "physicalVamp": champion_stats.get("physicalVamp"),
                    "power": champion_stats.get("power"),
                    "powerMax": champion_stats.get("powerMax"),
                    "powerRegen": champion_stats.get("powerRegen"),
                    "spellVamp": champion_stats.get("spellVamp"),
                }

                participant_champ_stats_rows.append(participant_champ_dict)

                participant_damage_dict = {
                    "match_id": match_id,
                    "event_number": i,
                    "participantId": participant.get("participantId"),
                    "timestamp": frame.get("timestamp"),
                    "magicDamageDone": damage_stats.get("magicDamageDone"),
                    "magicDamageDoneToChampions": damage_stats.get("magicDamageDoneToChampions"),
                    "magicDamageTaken": damage_stats.get("magicDamageTaken"),
                    "physicalDamageDone": damage_stats.get("physicalDamageDone"),
                    "physicalDamageDoneToChampions": damage_stats.get("physicalDamageDoneToChampions"),
                    "physicalDamageTaken": damage_stats.get("physicalDamageTaken"),
                    "totalDamageDone": damage_stats.get("totalDamageDone"),
                    "totalDamageDoneToChampions": damage_stats.get("totalDamageDoneToChampions"),
                    "totalDamageTaken": damage_stats.get("totalDamageTaken"),
                    "trueDamageDone": damage_stats.get("trueDamageDone"),
                    "trueDamageDoneToChampions": damage_stats.get("trueDamageDoneToChampions"),
                    "trueDamageTaken": damage_stats.get("trueDamageTaken"),
                }

                participant_damage_stats_rows.append(participant_damage_dict)

                other_stats_dict = {
                    "match_id": match_id,
                    "event_number": i,
                    "participantId": participant.get("participantId"),
                    "timestamp": frame.get("timestamp"),
                    "currentGold": participant.get("currentGold"),
                    "goldPerSecond": participant.get("goldPerSecond"),
                    "jungleMinionsKilled": participant.get("jungleMinionsKilled"),
                    "level": participant.get("level"),
                    "minionsKilled": participant.get("minionsKilled"),
                    "timeEnemySpentControlled": participant.get("timeEnemySpentControlled"),
                    "totalGold": participant.get("totalGold"),
                    "xp": participant.get("xp"),
                    "position_x": position.get("x"),
                    "position_y": position.get("y"),
                }

                participant_other_stats_rows.append(other_stats_dict)
                
        df_participants_champ_stats = pd.DataFrame(participant_champ_stats_rows)
        df_participants_damage_stats = pd.DataFrame(participant_damage_stats_rows)
        df_participants_other_stats = pd.DataFrame(participant_other_stats_rows)
 
         #double merge to get the full stats 
        participant_stats = df_participants_champ_stats.merge(df_participants_damage_stats, on=["match_id", "event_number","participantId", "timestamp"], how="left"
                                                              ).merge(df_participants_other_stats, on=["match_id","event_number", "participantId", "timestamp"], how="left"
                                                                )                 
        
        return {
            "start_end_game": pd.DataFrame(start_end_game_rows),
            "event_timeline": pd.DataFrame(event_timeline_rows),
            "assists": pd.DataFrame(assist_rows),
            "kills": pd.DataFrame(kills_rows),
            "monster_kills": pd.DataFrame(monster_kills_rows),
            "turret_kills": pd.DataFrame(turret_kills_rows),
            "bounty": pd.DataFrame(bounty_rows),
            "skill_level": pd.DataFrame(skill_level_rows),
            "item_history": pd.DataFrame(item_history_rows),
            "ward_history": pd.DataFrame(wards_history_rows),
            "participant_stats": pd.DataFrame(participant_stats)
        }
        





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
                    "hotStreak": False
                }
                )

        return pd.DataFrame(list_of_ranks_per_puuid)