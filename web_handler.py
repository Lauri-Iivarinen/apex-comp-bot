import requests
import asyncio
import aiohttp
import time
import threading
import json
from datetime import datetime

class Web_handler():

    async def poll_get_request(self, url, interval):
        
        async with aiohttp.ClientSession() as session:
            while datetime.now().day == self.today.day:
                async with session.get(self.lobby_url) as response:
                    res = await response.json()
                    # Process the response here
                    print(self.lobby_url)
                    print(response.status)
                    if res != self.results:
                        self.results = res
                        await self.print_res(res)
                await asyncio.sleep(interval)
        
        print("Loop has ended")
        self.loop.stop()
        #self.polling_thread.join()
        self.polling = False

    def run_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def start_polling_thread(self, url, interval):
        
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        asyncio.ensure_future(self.poll_get_request(url, interval))
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
        interval = 300
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
