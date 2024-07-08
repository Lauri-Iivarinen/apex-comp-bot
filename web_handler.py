import requests
import asyncio
import aiohttp
import time
import threading
import json
from datetime import datetime

class Web_handler():

    def get_url(self, type: str) -> str:
        if type == "results":
            return ""
        if type == "sp":
            return ""
        if type == "we":
            return ""
        return ""
    
    def is_different(self, we, we_c, sp, sp_c):
        if we != self.team_we:
            return True
        if we_c != self.contest_we:
            return True
        if sp != self.team_sp:
            return True
        if sp_c != self.contest_sp:
            return True
        return False

    async def poll_get_request(self, type: str, interval):
        async with aiohttp.ClientSession() as session:
            while datetime.now().hour < 23:
                async with session.get(self.lobby_url) as response:
                    res = await response.json()
                    # Process the response here
                    print(self.lobby_url)
                    print(response.status)
                    if "games" in res and res != self.results:
                        self.results = res
                        await self.print_res(res)
                        print("new result found, sleeping for 15 min")
                        await asyncio.sleep(900)
                        print('sleep over')
                await asyncio.sleep(interval)
        print("Loop has ended")
        self.loop.stop()
        #self.polling_thread.join()
        self.polling = False
    
    async def poll_get_request_drops(self, type: str, interval):
        async with aiohttp.ClientSession() as session:
            while datetime.now().hour < 20:
                # mp_rr_tropic_island_mu2
                print("drops")
                team_we = self.team_we
                contest_we = self.contest_we
                team_sp = self.team_sp
                contest_sp = self.contest_sp
                async with await session.get(f'https://overstat.gg/api/drops/{self.lobby}/mp_rr_desertlands_hu_lc') as response:
                    res = await response.json()
                    team_we, contest_we = self.get_team_drop(res)
                async with await session.get(f'https://overstat.gg/api/drops/{self.lobby}/mp_rr_tropic_island_mu2') as response:
                    res = await response.json()
                    team_sp, contest_sp = self.get_team_drop(res)
                if self.is_different(team_we, contest_we, team_sp, contest_sp):
                    print("DIFF")
                    print(team_we, team_sp, contest_sp, contest_we)
                    self.team_we = team_we
                    self.team_sp = team_sp
                    self.contest_we = contest_we
                    self.contest_sp = contest_sp
                    await self.print_drops(True, ["", self.team_we, self.team_sp], "", [False, self.contest_we, self.contest_sp], True)
                await asyncio.sleep(600)
        await asyncio.sleep(900)
        await self.poll_get_request("aa", 60)

    def run_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def start_polling_thread(self, url, interval):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        asyncio.ensure_future(self.poll_get_request_drops(self.lobby_url, interval))
        self.polling_thread = threading.Thread(target=self.run_event_loop)
        self.polling_thread.daemon = True  # This allows the thread to exit when the main program exits

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

    def set_lobby(self, url):
        self.lobby = self.parse_url(url)
        self.lobby_url = f'https://overstat.gg/api/stats/{self.lobby}/overall'

    def get_results(self, today: datetime):
        self.today = today
        #Vaihda niin ettei pollausta lopeteta vaan url vaan vaihtuu, pollaus lopetetan aikataulun mukaan
        print(self.polling)
        interval = 60
        if not self.polling:
            print("starting")
            self.polling = True
            self.start_polling_thread(f'https://overstat.gg/api/stats/{self.lobby}/overall', interval)

    
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
        drop_arr = list(map(lambda d: d["drop"], team))
        drop_arr.sort()
        for drop in drop_arr:
            if len(drop_str) != 0:
                drop_str = drop_str + "&"
            drop_str = drop_str + drop
        return drop_str.replace(" ", "_").lower(), contested

    def refresh_drops(self):
        self.drops_we = self.get_drops("mp_rr_desertlands_hu_lc")
        self.drops_sp = self.get_drops("mp_rr_tropic_island_mu2")
        self.team_we, self.contest_we = self.get_team_drop(self.drops_we)
        self.team_sp, self.contest_sp = self.get_team_drop(self.drops_sp)

    def __init__(self, url: str, team_name: str, print_res, print_drops) -> None:
        self.lobby = self.parse_url(url)
        self.team_name = team_name
        self.refresh_drops()
        self.polling = False
        self.lobby_url = f'https://overstat.gg/api/stats/{self.lobby}/overall'
        self.results = {}
        self.print_res = print_res
        self.print_drops = print_drops
