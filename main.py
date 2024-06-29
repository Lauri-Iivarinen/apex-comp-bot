import discord
from discord.ext import commands
from web_handler import Web_handler
from client import MyClient
from dotenv import load_dotenv
import os

def read_env():
    load_dotenv('.env')
    TOKEN = os.getenv('bot_token')
    IMG_CHANNEL_ID = os.getenv('img_bank_id')
    TEAM = os.getenv('team_name')
    return TOKEN, IMG_CHANNEL_ID, TEAM

def main():
    TOKEN, IMG_CHANNEL_ID, TEAM = read_env()
    intents = discord.Intents.default()
    intents.message_content = True

    client = MyClient(intents=intents)
    client.add_variables(IMG_CHANNEL_ID, TEAM)
    client.run(TOKEN)
    #wh = Web_handler("https://overstat.gg/tournament/108/6943.Lobby_2_6_27_2024")
    #wh.get_worlds_edge_drops()

if __name__ == '__main__':
    main()