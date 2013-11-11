from __future__ import unicode_literals

import random

from lib.constants import DATA_BLOB as d
from lib.constants import SPREAD_DATA_BLOB as sd
from lib.constants import NFL as nfl

class DataBlobFactory():
    def generate_data(self, timestamp=0, week=0, type="score"):
        if timestamp:
            if type == "spread":
                return {
                    "timestamp": timestamp,
                    "data": self._spread_data(week)
                }
            else:
                return {
                    "timestamp": timestamp,
                    "data": self._score_data(week)
                }
        else:
            if type == "spread":
                return self._spread_data(week)
            else:
                return self._score_data(week)

    def _score_data(self, week):
        return {
            d.GAME_WEEK: week,
            d.GAME_SEASON: nfl.YEAR,
            d.GAME_CLOCK: "12:34",
            d.GAME_DAY: "SUN",
            d.GAME_STATUS: "Pregame",
            d.GAME_TAG: "Pre0",
            d.GAME_TIME: "11:33",
            d.AWAY_NAME: self.__random_team(),
            d.AWAY_SCORE: 20,
            d.HOME_NAME: self.__random_team(),
            d.HOME_SCORE: 21,
            d.NFL_GAME_ID: self.__random_id(),
            d.SPREAD_MARGIN: 42.5,
            d.SPREAD_ODDS: 7.5
        }

    def _spread_data(self, week):
        return {
            d.GAME_WEEK: week,
            d.GAME_SEASON: nfl.YEAR,
            sd.SPREAD_OWNER: "MegaMan"
        }

    def __random_team(self):
        index = random.randint(0,len(nfl.TEAM_NAME)-1)

        return nfl.TEAM_NAME.values()[index]

    def __random_id(self):
        return random.randint(1000, 3000)
