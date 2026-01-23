import requests
import pandas as pd


puuid = pd.Series([
            "cJEsaUmbXGR3cMl_1RpPghEtI1PeSbiBdLyGsam8EVBQNBmdaJciZI9SFNERFBcRdu8l9b22-3GycA",
            "cJXXK6DUgKQzGcfZ4KOizTEcDF7FarsXAu4TyqGwb406msf001ln9oKcTRA-8abz4eiuvR__pCRaBA",
            "92BcB5BjkdGv0mYHu2cUdABaN-r1GCeOtuuEhI-3D-4cUk-XyOwJFJy3EmctU0uyS3HZAj0vDi-UOw",
            "n_TvRHWCwK_1oJmgCiF_3y1YyEsoH9gSfI-cBmz9J_Y6wq9jGVR-1i5Pbznj5vF0MhcxX4cBgbKAgw",
            "YH-Gl6RnQGRw4D5bHRjWX-FrRNUPbSnsv7G-sEG3KSLNGBllcWxvIdXzxkzrCbzeT5PxhBTuwTckOw",
            "He0w1rpV1E1RAWyyZMJhRoX2ZHBuNlFOhI9uTonfnz2BznPb9A5q2Yy0Ev9392E6OvcXathkRmORMQ",
            "SVy6V2h4-fMasrPMSBSKiux22aciLq3ZR7l8uDmwUc-oZqhPQ8xugihOfaYQCCExX9_dKA5WrGhIyQ",
            "lnyz846TOkYn8s12gFix2SpqliVungbIZqmLT_ZYg-1j3oVp5NcaojI1zi2xmRsSDLIhQApqF3W72Q",
            "bfU_8FeTt70SOmVQWPb26wYGN6Dn7PQZFSFiiGJbAIsK0cI0kBSmIgcfWNpsG4b2q5eRw1esh_kBgg",
            "Hc6OeF4U9Qm_3rKyaqkFAmKfZ33Wcq9moa53InJYEml7Hn7CgKDw60SndXwk9lCCxiqfyRjOURDJ6Q"
        ],name="puuid")


api_key = "RGAPI-d1fc28c4-e019-49b1-b768-8997e0650309"



list_of_ranks = []

def get_player_rank(api_key, puuid):


    
    for i in puuid:
        link = f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-puuid/{i}?api_key={api_key}"
        res = requests.get(link).json()

        if isinstance(res, list) and len(res) > 0:

            for entry in res:
                if entry.get("queueType") == "RANKED_SOLO_5x5":
                    solo_entry = entry
                    list_of_ranks.append(solo_entry)
        else: 
            # Liste war leer [] -> Spieler hat gar keinen Rang
            list_of_ranks.append(
                {
                "leagueId": None,
                "queueType": "RANKED_SOLO_5x5",
                "tier": None, 
                "rank": None, 
                "puuid": i,
                "leaguePoints": None, 
                "wins": None, 
                "losses": None,
                "veteran": False,
                "inactive": False,
                "freshBlood": None,
                "hotstreak": False
            }
            )


    return print(pd.DataFrame(list_of_ranks).tail())


get_player_rank(api_key= api_key, puuid = puuid)