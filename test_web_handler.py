import unittest
from web_handler import Web_handler

class Test_web_handler(unittest.TestCase):

    def setUp(self):
        self.web_handler = Web_handler("https://overstat.gg/tournament/108/6943.Lobby_2_6_27_2024/drops/storm-point", "REBELS")

    def test_parse_url(self):
        self.assertEqual(self.web_handler.parse_url("https://overstat.gg/tournament/108/6943.Lobby_2_6_27_2024/drops/storm-point"), "6943")
        self.assertEqual(self.web_handler.parse_url("bad_url"), "")
    
    def test_get_team_drop(self):
        drops = {"OOREDOO": [{"teamName": "OOREDOO","map": "mp_rr_tropic_island_mu2","color": "#1a4768","drop": "Zeus Station"}],"REBELS": [{"teamName": "REBELS","map": "mp_rr_tropic_island_mu2","color": "#764b01","drop": "Echo MD"}]}
        self.assertEqual(self.web_handler.get_team_drop(drops), ("echo_md" ,False),)
        drops = {"OOREDOO": [{"teamName": "OOREDOO","map": "mp_rr_tropic_island_mu2","color": "#1a4768","drop": "Zeus Station"}],"REBELS": [{"teamName": "REBELS","map": "mp_rr_tropic_island_mu2","color": "#1a4768","drop": "Zeus Station"},{"teamName": "REBELS","map": "mp_rr_tropic_island_mu2","color": "#764b01","drop": "Echo MD"}]}
        self.assertEqual(self.web_handler.get_team_drop(drops), ("zeus_station&echo_md", True))
    
    def test_are_we_contested(self):
        drops = {"OOREDOO": [{"teamName": "OOREDOO","map": "mp_rr_tropic_island_mu2","color": "#1a4768","drop": "Zeus Station"}],"REBELS": [{"teamName": "REBELS","map": "mp_rr_tropic_island_mu2","color": "#764b01","drop": "Echo MD"}]}
        self.assertEqual(self.web_handler.are_we_contested(drops, drops["REBELS"]), False)
        drops = {"OOREDOO": [{"teamName": "OOREDOO","map": "mp_rr_tropic_island_mu2","color": "#1a4768","drop": "Zeus Station"}],"REBELS": [{"teamName": "REBELS","map": "mp_rr_tropic_island_mu2","color": "#1a4768","drop": "Zeus Station"},{"teamName": "REBELS","map": "mp_rr_tropic_island_mu2","color": "#764b01","drop": "Echo MD"}]}
        self.assertEqual(self.web_handler.are_we_contested(drops, drops["REBELS"]), True)
