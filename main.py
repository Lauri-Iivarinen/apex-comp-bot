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
    RESULTS_CHANNEL = os.getenv('results_channel')
    LOOT_PATH_CHANNEL_ID = os.getenv('loot_path_channel_id')
    TEAM_ROLE_TAG_ID = os.getenv('role_tag_id')
    ARCHIVE_CHANNEL_ID = os.getenv('archive_channel_id')
    return TOKEN, IMG_CHANNEL_ID, TEAM, RESULTS_CHANNEL, LOOT_PATH_CHANNEL_ID, TEAM_ROLE_TAG_ID, ARCHIVE_CHANNEL_ID

def main():
    TOKEN, IMG_CHANNEL_ID, TEAM, RESULTS_CHANNEL, LOOT_PATH_CHANNEL_ID, TEAM_ROLE_TAG_ID, ARCHIVE_CHANNEL_ID = read_env()
    intents = discord.Intents.default()
    intents.message_content = True

    client = MyClient(intents=intents)
    client.add_variables(IMG_CHANNEL_ID, TEAM, RESULTS_CHANNEL, LOOT_PATH_CHANNEL_ID, TEAM_ROLE_TAG_ID, ARCHIVE_CHANNEL_ID)
    client.run(TOKEN)
    #wh = Web_handler("https://overstat.gg/tournament/108/6943.Lobby_2_6_27_2024")
    #wh.get_worlds_edge_drops()

if __name__ == '__main__':
    main()