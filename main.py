import discord
from discord.ext import commands
from client import MyClient
from dotenv import load_dotenv
import os

def read_env():
    load_dotenv('.env')
    TOKEN = os.getenv('bot_token')
    IMG_CHANNEL_ID = os.getenv('img_bank_id')
    return TOKEN, IMG_CHANNEL_ID

def main():
    TOKEN, IMG_CHANNEL_ID = read_env()
    intents = discord.Intents.default()
    intents.message_content = True

    client = MyClient(intents=intents)
    client.add_variables(IMG_CHANNEL_ID)
    client.run(TOKEN)

if __name__ == '__main__':
    main()