import requests


class Dashboard_Images:

    
    def __init__(self):
        self.item_link = "https://ddragon.leagueoflegends.com/cdn/16.18.1/data/en_US/item.json"
        self.rune_link = "https://ddragon.leagueoflegends.com/cdn/16.18.1/data/en_US/runesReforged.json"
        self.champion_link = "https://ddragon.leagueoflegends.com/cdn/16.18.1/data/en_US/champion.json" 

        self.download_link_champion = f"https://ddragon.leagueoflegends.com/cdn/16.18.1/img/champion/"
        self.download_link_item = f"https://ddragon.leagueoflegends.com/cdn/16.18.1/img/item/"
        self.download_link_runes = f"https://ddragon.leagueoflegends.com/cdn/img/"

    def Champion(self) -> list:

        champion_data = []
        res = requests.get(self.champion_link).json()

        champion = res["data"]

        for champ in champion.values():
            champion_data.append({
                "champ_name": champ["name"],
                "champ_key": champ["key"],
                "champ_id": champ["id"],
                "icon_link": self.download_link_champion + champ["image"]["full"]
            })
        
        return champion_data


    def Item(self)-> list:
        item_data = []
        res = requests.get(self.item_link).json()

        items = res["data"]

        for item in items.values():
            item_data.append({

                "item_id":item,
                "item_name": item["name"],
                "item_cost": item["gold"]["base"],
                "item_sell": item["gold"]["sell"],
                "icon_link": self.download_link_item + item["image"]["full"]
            })
        return item_data

    def Rune(self) -> list:
        rune_data = []
        trees = requests.get(self.rune_link).json()

        for tree in trees:                          #  Precision, Domination, ...
            for i, slot in enumerate(tree["slots"]):  # Each tree has several slots 
                for r in slot["runes"]:               # And each tree has several rune options for that slot
                    rune_data.append({
                        "rune_id": r["id"],
                        "rune_name": r["name"],
                        "tree": tree["key"],
                        "slot_number": i,           
                        "icon_link": self.download_link_runes + r["icon"]
                    })

        return rune_data




        
