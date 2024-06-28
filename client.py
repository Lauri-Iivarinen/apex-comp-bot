import discord

class MyClient(discord.Client):

    def allowed_channel(self, channel: str):
        print(channel.name)
        chls = ['dev', 'dev2']
        if channel.name in chls:
            return True
        return False
        

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        if message.author == self.user:
            return
        if not self.allowed_channel(message.channel):
            return
        
        print(f'Message from {message.author} in {message.channel}: {message.content}')
        
        await message.channel.send(f'{message.author} sent: {message.content}')