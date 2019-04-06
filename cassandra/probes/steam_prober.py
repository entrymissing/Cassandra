import os
import time

from cassandra.probes import base_prober
from steamwebapi.api import ISteamUser, IPlayerService

__PROBE_NAME = ['SteamProber']

CREDENTAL_FILE = 'steam_api_key'

class SteamProber(base_prober.BaseProber):
    def setup(self):
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        credential_path = os.path.join(credential_dir,
                                       CREDENTAL_FILE)
        with open(credential_path) as api_file:
            self.steam_api_key = api_file.read()
        # print(self.steam_api_key)


    def collect_data(self):
        now = time.time()
        data = {}

        steamuserinfo = ISteamUser(steam_api_key=self.steam_api_key)
        steamid = steamuserinfo.resolve_vanity_url("entrymissing")['response']['steamid']
        playerinfo = IPlayerService(steam_api_key=self.steam_api_key)
        played_games = playerinfo.get_recently_played_games(steamid)['response']
        playtime = [game['playtime_2weeks'] for game in played_games['games']]
        owned_games = playerinfo.get_owned_games(steamid)['response']

        data[self.prefix + '.game_count_2w'] = [(now, played_games['total_count'])]
        data[self.prefix + '.minutes_played_2w'] = [(now, sum(playtime))]
        data[self.prefix + '.owned_games'] = [(now, owned_games['game_count'])]

        return data
