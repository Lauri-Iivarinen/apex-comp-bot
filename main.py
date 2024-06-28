import discord
from discord.ext import commands
from client import MyClient
from dotenv import load_dotenv
import os

def read_env():
    load_dotenv('.env')
    TOKEN = os.getenv('bot_token')

    return TOKEN

def main():
    TOKEN = read_env()
    intents = discord.Intents.default()
    intents.message_content = True

    client = MyClient(intents=intents)
    client.run(TOKEN)

if __name__ == '__main__':
    main()