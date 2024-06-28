import discord
from discord.ext import commands
from datetime import datetime

class MyClient(discord.Client):

    def __init__(self, *, intents, **options) -> None:
        super().__init__(intents=intents, **options)

    def add_variables(self, img_bank_id):
        self.img_bank_id = img_bank_id

    def allowed_channel(self, channel):
        #print(channel.name)
        chls: list[str] = ['lootpaths-dev']
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
        #print(messages_arr[0].embeds)
        #print(messages_arr[0].attachments)
        #print(messages_arr)
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
        dt = datetime.now()
        return f"**Drops for {dt.day}.{dt.month}.{dt.year}:**"
    
    async def command_drops(self, command, message):
        if message.channel.name != 'lootpaths-dev':
            return
        await self.clear_drops_channel(message.channel)
        await message.channel.send(self.get_drops_creation_date())
        for i in range(1, len(command)):
            await self.print_image_to_channel(command[i], message.channel)

    async def on_message(self, message):
        if message.author == self.user:
            return
        if not self.allowed_channel(message.channel):
            return
        if message.content[0] == '!':
            command = message.content.split(' ')
            if command[0] == '!drops':
                await self.command_drops(command, message)
        
        
            