import requests
import asyncio
import aiohttp
import time
import threading
import json
from datetime import datetime

class Web_handler():

    def get_url(self, type: str) -> str:
        #lisää uudet mapit
        if type == "results":
            return ""
        if type == "sp":
            return ""
        if type == "we":
            return ""
        return ""
    
    def is_different(self, we, we_c, sp, sp_c):
        #¤lisää uudet mapit
        if we != self.team_we:
            return True
        if we_c != self.contest_we:
            return True
        if sp != self.team_sp:
            return True
        if sp_c != self.contest_sp:
            return True
        return False
    
    def games_remaining(self) -> bool:
        if "games" not in self.results:
            return True
        return len(self.results["games"]) < self.game_count

    def is_not_over(self, end: datetime, current: datetime) -> bool:
        if end.hour <= current.hour and end.minute <= current.minute:
            return False
        return True
    
    async def stop_polling(self):
        print("Loop has ended")
        self.loop.stop()
        #self.polling_thread.join()
        self.polling = False

    async def poll_get_request(self, type: str, interval, end: datetime):
        async with aiohttp.ClientSession() as session:
            while self.is_not_over(end, datetime.now()) and self.games_remaining():
                try:
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
                        if not self.games_remaining(): # if gane count reaches max, end loop without 15min delay
                            break
                except:
                    print("Fetching results failed")
                await asyncio.sleep(interval)
        await self.stop_polling()
        await self.archive_result(self.results)
    
    async def poll_get_request_drops(self, start, end, type: str, interval):
        async with aiohttp.ClientSession() as session:
            while self.is_not_over(start, datetime.now()):
                # mp_rr_tropic_island_mu2
                print("drops")
                team_we = self.team_we
                contest_we = self.contest_we
                team_sp = self.team_sp
                contest_sp = self.contest_sp
                
                try:
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
                except:
                    print("Error fetching drops")
                await asyncio.sleep(600)
        print("polling drops over, sleeping 15min")
        await asyncio.sleep(900)
        await self.poll_get_request("aa", 60, end)

    def run_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def start_polling_thread(self, start, end, url, interval):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        asyncio.ensure_future(self.poll_get_request_drops(start, end, self.lobby_url, interval))
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

    # Starts the polling cycle for drops into game results
    def get_results(self, today: datetime, games: int, start, end):
        self.today = today
        self.games = games
        #Vaihda niin ettei pollausta lopeteta vaan url vaan vaihtuu, pollaus lopetetan aikataulun mukaan
        print(self.polling)
        interval = 60
        if not self.polling:
            print("starting")
            self.polling = True
            self.start_polling_thread( start, end, f'https://overstat.gg/api/stats/{self.lobby}/overall', interval)

    
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

        for map in self.map_hash.keys():
            print(map)
            #looppaa mappi kerrallaan
            drops = self.get_drops(self.map_hash[map])
            team_drop = self.get_team_drop(drops)
            self.drops_map[map] = drops
            self.team_drops_map[map] = team_drop
        self.drops_we = self.get_drops("mp_rr_desertlands_hu_lc")
        self.drops_sp = self.get_drops("mp_rr_tropic_island_mu2")
        self.team_we, self.contest_we = self.get_team_drop(self.drops_we)
        self.team_sp, self.contest_sp = self.get_team_drop(self.drops_sp)

        print(self.team_drops_map)
        print(self.drops_map)
    
    def set_game_count(self, count: int):
        count = int(count)
        self.game_count = count

    def __init__(self, url: str, team_name: str, print_res, print_drops, archive_result) -> None:
        self.map_hash = {
            "op": "mp_rr_olympus_mu2_v2",
            "dc": "mp_rr_district",
            "kc": "mp_rr_canyonlands_hu",
            "we": "mp_rr_desertlands_hu_lc",
            "sp": "mp_rr_tropic_island_mu2",
            "bm": "mp_rr_divided_moon_mu1",
        }
        self.team_drops_map = {}
        self.drops_map = {}
        self.lobby = self.parse_url(url)
        self.team_name = team_name
        self.refresh_drops()
        self.polling = False
        self.lobby_url = f'https://overstat.gg/api/stats/{self.lobby}/overall'
        self.results = {}
        self.print_res = print_res
        self.print_drops = print_drops
        self.archive_result = archive_result
        self.game_count = 6
        
