import discord
from discord.ext import commands
from datetime import datetime
from web_handler import Web_handler
import time
import threading
import asyncio
import aiohttp

class MyClient(discord.Client):

    def __init__(self, *, intents, **options) -> None:
        super().__init__(intents=intents, **options)

    def add_variables(self, img_bank_id, team_name):
        self.img_bank_id = img_bank_id
        self.team_name = team_name

    def allowed_channel(self, channel):
        #print(channel.name)
        chls: list[str] = ['lootpaths-dev', 'imagebank-dev']
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
    
    async def clear_drops_channel(self, channel):
        await channel.purge()

    def get_drops_creation_date(self):
        self.today = dt = datetime.now()
        return f"# Drops for {dt.day}.{dt.month}.{dt.year}: #"
    
    def print_res(self, res):
        print(res)

    async def poll_results(self):
        dt = datetime.now()
        if dt.day != self.today.day:
            return
        res = self.wh.get_results(None)
        #print(res["total"])
        #time.sleep(10)
        
    
    async def command_drops(self, command, message, contest_arr = [False, False, False], detailed = False, details = ["", "Worlds Edge:", "Storm Point:", "Broken Moon:", "Olympus:", "Kings Canyon:"]):
        if message.channel.name != 'lootpaths-dev':
            return
        await self.clear_drops_channel(message.channel)
        await message.channel.send(self.get_drops_creation_date())
        for i in range(1, len(command)):
            if detailed:
                msg_str: str = details[i]
                if contest_arr[i]:
                    msg_str = msg_str.replace(':', ", :sos: **CONTESTED** :sos::")
                await message.channel.send(msg_str)
            await self.print_image_to_channel(command[i], message.channel)
    
    async def command_lobby(self, command, message):
        try:
            self.wh.set_lobby(command[1])
        except AttributeError:
            self.wh = Web_handler(command[1], self.team_name)

        await self.command_drops(["", self.wh.team_we, self.wh.team_sp], message, [False, self.wh.contest_we, self.wh.contest_sp], True)
        await self.poll_results()
    
    async def print_help_text(self, channel):
        await channel.send(
        f'Commands:\n```!help -> this message(lol)\n\n!drops $drop1 $drop2... -> prints out as many drops as you need, needs exact match with imagebank names\n\n!lobby $url -> lobby url given in EXO, prints out drop spots for team {self.team_name}```')

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content == '!help':
                await self.print_help_text(message.channel)
        if not self.allowed_channel(message.channel):
            return
        if message.content[0] == '!':
            command = message.content.split(' ')
            if command[0] == '!drops':
                await self.command_drops(command, message)
            elif command[0] == '!lobby':
                await self.command_lobby(command, message)
            elif command[0] == '!th':
                print(threading.active_count())
        if message.channel.name == 'imagebank-dev':
            await self.get_all_imgs_to_map()
        
        
            