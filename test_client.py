import unittest
from client import MyClient
from test_data import played_lobby, empty_lobby
import discord
from datetime import datetime

class Test_client(unittest.TestCase):

    def setUp(self):
        self.client = MyClient(intents = discord.Intents.default())
        self.client.add_variables('123456', 'REBELS', 'result-chl', '234567')
    
    def test_get_placement(self):
        self.assertEqual(self.client.get_placement(empty_lobby), '-')
        self.assertEqual(self.client.get_placement(played_lobby), '12th - 1pts behind 11th')
    
    def test_format_placement(self):
        self.assertEqual(self.client.format_placement(1), '1st')
        self.assertEqual(self.client.format_placement(2), '2nd')
        self.assertEqual(self.client.format_placement(3), '3rd')
        self.assertEqual(self.client.format_placement(4), '4th')

    def test_format_details(self):
        self.assertEqual(self.client.format_details(1, 'abc'), '1  ')
        self.assertEqual(self.client.format_details('4', 'abcde'), '4    ')
        self.assertEqual(self.client.format_details('11', 'abcde'), '11   ')
    
    def test_get_game_results(self):
        self.assertEqual(self.client.get_game_results([]), '```Game Plcmt Pts Kills Dmg\n```')
        games = played_lobby["games"][0:2]
        self.assertEqual(self.client.get_game_results(games), '```Game Plcmt Pts Kills Dmg\n1    3     12  5     2643\n2    17    0   0     205\n```')
    
    def test_get_player_results(self):
        pls = played_lobby["teams"][11]["player_stats"][2:]
        self.assertEqual(self.client.get_player_results({"player_stats": pls}), '**Prince**:\n```Kills Knocks Damage Accuracy\n7     8      2257   0.16```\n')
    
    def test_find_team(self):
        self.assertEqual(self.client.find_team(played_lobby['teams'])["teamId"], 13)
        self.client.add_variables('123456', 'bad_name', 'result-chl', '234567')
        self.assertEqual(self.client.find_team(played_lobby['teams']), {})

    def test_get_drops_creation_date(self):
        dt = datetime.now()
        self.assertTrue(f'{dt.day}.' in self.client.get_drops_creation_date())
        self.assertTrue(f'{dt.year}:' in self.client.get_drops_creation_date())