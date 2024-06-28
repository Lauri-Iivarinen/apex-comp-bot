import discord

class MyClient(discord.Client):

    def allowed_channel(self, channel):
        print(channel.name)
        chls = ['dev2']
        if channel.name in chls:
            return True
        return False
        
    async def print_channel(self, msg_id, to_chl):
        chl_id = 1256299995192229990
        channel = await self.fetch_channel(chl_id)
        res = await channel.fetch_message(msg_id)
        print(res.content)
        st = res.content.split('\n')[1]
        await to_chl.send(f'{st}')

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        if message.author == self.user:
            return
        if not self.allowed_channel(message.channel):
            return
        
        #print(f'Message from {message.author} in {message.channel}: {message.content}')
        await self.print_channel(message.content, message.channel)
        #await message.channel.send(f'{message.author} sent: {message.content}')