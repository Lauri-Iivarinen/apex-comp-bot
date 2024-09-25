import discord
from discord.ext import commands
from datetime import datetime
from web_handler import Web_handler
import threading

class MyClient(discord.Client):

    def __init__(self, *, intents, **options) -> None:
        super().__init__(intents=intents, **options)

    def add_variables(self, img_bank_id, team_name, results_channel, loot_path_channel_id, role_tag_id, archive_channel_id):
        self.img_bank_id = img_bank_id
        self.team_name = team_name
        self.results_channel_id = results_channel
        self.loot_path_channel_id = loot_path_channel_id
        self.role_tag_id = role_tag_id
        self.archive_channel_id = archive_channel_id

    def allowed_channel(self, channel):
        #print(channel.name)
        chls: list[str] = ['img-bank', 'history', 'lootpaths-dev', 'imagebank-dev', 'dev', 'general', 'loot-pathit']
        if channel.name in chls:
            return True
        return False
        
    async def print_image_to_channel(self, msg_tag, to_chl):
        if msg_tag in self.messages:
            res = self.messages[msg_tag]
            await to_chl.send(res)
    
    def get_image_from_message(self, message):
        content = message.content.split('\n')
        if len(content) == 2:
            return content
        elif '\n' not in message.content and len(message.attachments) == 1:
            return [message.content, message.attachments[0].url]
        return [message.content, f'Cannot find image for {message.content}']

    async def get_all_imgs_to_map(self):
        channel = await self.fetch_channel(self.img_bank_id)
        messages_arr = [message async for message in channel.history(limit=100)]
        messages = list(map(lambda m: self.get_image_from_message(m), messages_arr))
        msgs = {}
        for m in messages:
            msgs[m[0]] = m[1]
        self.messages: dict[str: str] = msgs

    async def on_ready(self):
        await self.get_all_imgs_to_map()
        print(f'Logged on as {self.user}!')
    
    async def clear_drops_channel(self):
        chl = await self.fetch_channel(self.loot_path_channel_id)
        await chl.purge()

    def get_drops_creation_date(self):
        self.today = dt = datetime.now()
        return f"# Drops for {dt.day}.{dt.month}.{dt.year}: #"

    def find_team(self, teams: list[dict]) -> dict:
        team = {}
        for t in teams:
            if t["name"] == self.team_name:
                return t
        return team

    def format_details(self, value, format_to) -> str:
        value = str(value)
        string = f"{value}"
        spc = " "
        string = string + spc*(len(format_to)-len(value))
        return string
    
    def get_player_results(self, team: dict) -> str:
        res = f''
        for pl in team["player_stats"]:
            res = res + f'**{pl["name"]}**:\n```Kills Knocks Damage Hit%\n{self.format_details(pl["kills"], "Kills ")}{self.format_details(pl["knockdowns"], "Knocks ")}{self.format_details(pl["damageDealt"], "Damage ")}{pl["accuracy"]}```\n'
        return res
    
    def get_game_results(self, games: list[dict]) -> str:
        game_str = f'```Game Plcmt Pts Kills Dmg\n'
        for i in range(0, len(games)):
            game = games[i]
            team = self.find_team(game["teams"])
            team = team["overall_stats"]
            game_str = game_str + f'{self.format_details(i+1, "Game ")}{self.format_details(team["teamPlacement"], "Plcmt ")}{self.format_details(team["score"], "Pts ")}{self.format_details(team["kills"], "Kills ")}{team["damageDealt"]}\n'
        game_str = game_str + '```'
        return game_str
    
    #Only 20 teams in apex so no need to worry about 21st place etc
    def format_placement(self, num) -> str:
        if num == 1:
            return "1st"
        elif num == 2:
            return "2nd"
        elif num == 3:
            return "3rd"
        return f"{num}th"
    
    def get_placement(self, results: dict) -> str:
        if 'games' not in results:
            return '-'
        res = f""
        teams = results["teams"]
        for i in range(0, len(teams)):
            if teams[i]["name"] == self.team_name and i == 0:
                return "1st"
            elif teams[i]["name"] == self.team_name:
                prev_team = teams[i-1]["overall_stats"]
                team = teams[i]["overall_stats"]
                return f'{self.format_placement(i+1)} - {(prev_team["score"] - team["score"])}pts behind {self.format_placement(i)}'
        return "-"

    def format_link(self, link: str) -> str:
        res = link.split('/')
        res_str = ''
        for i in range(0,6):
            res_str = res_str + res[i] + '/'
        return res_str

    async def archive_result(self, result: dict):
        channel = await self.fetch_channel(self.archive_channel_id)
        dt = datetime.now()
        msg = await channel.send(f"<{self.format_link(self.current_link)}>")
        thrd = await channel.create_thread(name=f'{dt.day}.{dt.month}.{dt.year}', message=msg)
        await thrd.send(self.get_placement(result))

    def format_results(self, results: dict) -> str:
        games_arr = []
        if 'games' in results:
            games_arr = results['games']
        games_played = len(games_arr)
        quality_score = '-'
        if 'analytics' in results and 'qualityScore' in results["analytics"]:
            quality_score = str(round(results['analytics']['qualityScore'], 2))
        team = self.find_team(results['teams'])
        overall_points = team["overall_stats"]["score"]
        player_results: str = self.get_player_results(team)
        dt = self.today
        game_results = ''
        if 'games' in results:
            game_results = self.get_game_results(results["games"])
        return f'# SCRIMS {dt.day}.{dt.month}.{dt.year} - {games_played}/{self.wh.game_count} # \n**Quality:** {quality_score}\n**Points:** {overall_points} pts\n**Placement:** {self.get_placement(results)}\n## Players: ## \n{player_results}## Games: ##\n{game_results}'
    
    async def print_res(self, res):
        channel = await self.fetch_channel(self.results_channel_id)
        print('printing results in client')
        messages = [message async for message in channel.history(limit=100)]
        if len(messages) != 1: # Channel either has no messages yet or channel has been filled with trash
            await channel.purge()
            await channel.send(self.format_results(res))
            return
        message = messages[0]
        await message.edit(content=self.format_results(res))
        

    def print_drops(self, res):
        print(res)

    async def poll_results(self, games: int, start, end):
        dt = datetime.now()
        if dt.day != self.today.day:
            return
        res = self.wh.get_results(self.today, games, start, end)
        #print(res["total"])
        #time.sleep(10)
    
    async def command_drops(self, alert: bool, command, message, contest_arr = [False, False, False], detailed = False, details = ["", "Worlds Edge:", "Storm Point:", "Broken Moon:", "Olympus:", "Kings Canyon:"]):
        #New dynamic map printing inc
        print(command)
        channel = await self.fetch_channel(self.loot_path_channel_id)
        await self.clear_drops_channel()
        await channel.send(self.get_drops_creation_date())
        if alert:
            await channel.send(f"<@&{self.role_tag_id}> there's been a change in contest or landings")
        for i in range(1, len(command)):
            if detailed and command[i] != '':
                msg_str: str = details[i]
                if contest_arr[i]:
                    msg_str = msg_str.replace(':', ", :sos: **CONTESTED** :sos::")
                await channel.send(msg_str)
            await self.print_image_to_channel(command[i], channel)
    
    async def command_lobby(self, command: list[str], message):
        current_time = datetime.now()
        start_time = datetime(current_time.year, current_time.month, current_time.day, 20, 0, 0)
        end_time = datetime(current_time.year, current_time.month, current_time.day, 23, 0, 0)
        games = 6
        if len(command) > 2:
            # Custom configs
            for i in range(2,len(command)):
                if command[i] == 'start=':
                    start_str = command[i].split(" ")[1].split(":")
                    start_time = datetime(current_time.year, current_time.month, current_time.day, int(start_str[0]), int(start_str[1]), 0)
                if command[i] == 'end=':
                    end_str = command[i].split(" ")[1].split(":")
                    datetime(current_time.year, current_time.month, current_time.day, int(end_str[0]), int(end_str[1]), 0)
                if command[i] == 'games=':
                    games = int(command[i].split(" ")[1])
        self.current_link = command[1]
        #await self.archive_result({})
        await message.add_reaction('\U00002705')
        try:
            self.wh.set_lobby(command[1])
        except AttributeError:
            self.wh = Web_handler(command[1], self.team_name, self.print_res, self.command_drops, self.archive_result)
        await self.command_drops(False, ["", "", ""], message, [False, False, False], True)
        await self.poll_results(games, start_time, end_time)
    
    async def print_help_text(self, channel):
        await channel.send(
        f'Commands:\n```!help -> this message(lol)\n\n!drops $drop1 $drop2... -> prints out as many drops as you need, needs exact match with imagebank names\n\n!lobby $url -> lobby url given in EXO, prints out drop spots for team {self.team_name}```')

    async def on_message(self, message):
        if message.author == self.user or not self.allowed_channel(message.channel):
            return
        if message.content == '!help':
            await self.print_help_text(message.channel)
        if len(message.content) > 0 and message.content[0] == '!':
            command = message.content.split(' ')
            if command[0] == '!drops':
                await self.command_drops(command, message)
            elif command[0] == '!lobby':
                await self.command_lobby(command, message)
            elif command[0] == '!stop':
                try:
                    await self.wh.stop_polling()
                    await message.add_reaction('\U00002705')
                except:
                    print("No webhandler")
            elif command[0] == '!games':
                try:
                    self.wh.set_game_count(1)
                    await message.add_reaction('\U00002705')
                except:
                    print("No webhandler")
            elif command[0] == '!test':
                await self.archive_result_test(command[1])
            elif command[0] == '!th':
                print(threading.active_count())
        if message.channel.name == 'imagebank-dev':
            await self.get_all_imgs_to_map()
        
        
            