import requests

class Web_handler():

    def parse_url(self, url: str):
        if "tournament" not in url:
            return ""
        lobby = url.split('tournament')[1].split('/')[2].split('.')[0]
        return lobby
    
    def get_drops(self, map:str):
        res = requests.get(f'https://overstat.gg/api/drops/{self.lobby}/{map}')
        if res.status_code != 200:
            return {}
        res = res.json()
        return res
    
    def are_we_contested(self, drops, team_drops) -> bool:
        team_drops = list(map(lambda t: t["drop"], team_drops))
        for team in drops:
            if team != self.team_name:
                for drp in drops[team]:
                    if drp["drop"] in team_drops:
                        return True
        return False
    
    def get_team_drop(self, drops: dict[str: list[dict[str: str]]]):
        if self.team_name not in drops:
            return "", False
        team = drops[self.team_name]
        contested: bool = self.are_we_contested(drops, team)
        drop_str = ""
        for drop in team:
            if len(drop_str) != 0:
                drop_str = drop_str + "&"
            drop_str = drop_str + drop["drop"]
        return drop_str.replace(" ", "_").lower(), contested

    def refresh_drops(self):
        self.drops_we = self.get_drops("mp_rr_desertlands_hu_lc")
        self.drops_sp = self.get_drops("mp_rr_tropic_island_mu2")
        self.team_we, self.contest_we = self.get_team_drop(self.drops_we)
        self.team_sp, self.contest_sp = self.get_team_drop(self.drops_sp)

    def __init__(self, url: str, team_name: str) -> None:
        self.lobby = self.parse_url(url)
        self.team_name = team_name
        self.refresh_drops()
