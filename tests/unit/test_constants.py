#! /usr/bin/env python

from __future__ import unicode_literals

import datetime
import unittest

from lib.constants import CONSTANTS as c
from lib.constants import DATA_BLOB as db
from lib.constants import HTTP_CODE as http_code
from lib.constants import NFL as n
from lib.constants import PARAM_TYPES as pt
from lib.constants import SCOREBOARD as sb
from lib.constants import SPREAD_DATA_BLOB as sd

class TestConstants(unittest.TestCase):
    def test_days(self):
        self.assertEqual(
            c.DAYS["MON"],
            0)
        self.assertEqual(
            c.DAYS["TUE"],
            1)
        self.assertEqual(
            c.DAYS["WED"],
            2)
        self.assertEqual(
            c.DAYS["THU"],
            3)
        self.assertEqual(
            c.DAYS["FRI"],
            4)
        self.assertEqual(
            c.DAYS["SAT"],
            5)
        self.assertEqual(
            c.DAYS["SUN"],
            6)

    def test_encoding(self):
        self.assertEqual(
            c.ENCODING,
            "UTF-8")

    def test_memcache_threshold(self):
        self.assertEqual(
            c.MEMCACHE_THRESHOLD,
            300)

class TestDataBlob(unittest.TestCase):
    def test_data_blob(self):
        self.assertEqual(
            db.AWAY_NAME,
            "away_name")
        self.assertEqual(
            db.AWAY_SCORE,
            "away_score")
        self.assertEqual(
            db.GAME_CLOCK,
            "game_clock")
        self.assertEqual(
            db.GAME_DAY,
            "game_day")
        self.assertEqual(
            db.GAME_SEASON,
            "year")
        self.assertEqual(
            db.GAME_STATUS,
            "game_status")
        self.assertEqual(
            db.GAME_TAG,
            "game_tag")
        self.assertEqual(
            db.GAME_TIME,
            "game_time")
        self.assertEqual(
            db.GAME_WEEK,
            "week")
        self.assertEqual(
            db.HOME_NAME,
            "home_name")
        self.assertEqual(
            db.HOME_SCORE,
            "home_score")
        self.assertEqual(
            db.NFL_GAME_ID, 
            "game_id")
        self.assertFalse(
            hasattr(db, "MISC_PICKS"))
        self.assertFalse(
            hasattr(db, "MISC_STATS"))
        self.assertEqual(
            db.SPREAD_MARGIN,
            "spread_margin")
        self.assertEqual(
            db.SPREAD_ODDS,
            "spread_odds")
        self.assertFalse(
            hasattr(db, "SPREAD_OWNER"))
        self.assertFalse(
            hasattr(db, "SPREAD_WINNER"))
        self.assertEqual(
            db.TIMESTAMP,
            "timestamp")

class TestHttpCode(unittest.TestCase):
    def test_http_code(self):
        self.assertEqual(
            http_code.OK,
            200)
        self.assertEqual(
            http_code.CREATED,
            201)
        self.assertEqual(
            http_code.NOT_FOUND,
            404)
        self.assertEqual(
            http_code.INTERNAL_SERVER_ERROR,
            500)

class TestNfl(unittest.TestCase):
    def test_nfl(self):
        self.assertEqual(
            n.TEAM_NAME["ARIZONA"],
            "ARI")
        self.assertEqual(
            n.TEAM_NAME["ATLANTA"],
            "ATL")
        self.assertEqual(
            n.TEAM_NAME["BALTIMORE"],
            "BAL")
        self.assertEqual(
            n.TEAM_NAME["BUFFALO"],
            "BUF")
        self.assertEqual(
            n.TEAM_NAME["CAROLINA"],
            "CAR")
        self.assertEqual(
            n.TEAM_NAME["CHICAGO"],
            "CHI")
        self.assertEqual(
            n.TEAM_NAME["CINCINNATI"],
            "CIN")
        self.assertEqual(
            n.TEAM_NAME["CLEVELAND"],
            "CLE")
        self.assertEqual(
            n.TEAM_NAME["DALLAS"],
            "DAL")
        self.assertEqual(
            n.TEAM_NAME["DENVER"],
            "DEN")
        self.assertEqual(
            n.TEAM_NAME["DETROIT"],
            "DET")
        self.assertEqual(
            n.TEAM_NAME["GREEN BAY"],
            "GB")
        self.assertEqual(
            n.TEAM_NAME["HOUSTON"],
            "HOU")
        self.assertEqual(
            n.TEAM_NAME["INDIANAPOLIS"],
            "IND")
        self.assertEqual(
            n.TEAM_NAME["JACKSONVILLE"],
            "JAC")
        self.assertEqual(
            n.TEAM_NAME["KANSAS CITY"],
            "KC")
        self.assertEqual(
            n.TEAM_NAME["MIAMI"],
            "MIA")
        self.assertEqual(
            n.TEAM_NAME["MINNESOTA"],
            "MIN")
        self.assertEqual(
            n.TEAM_NAME["NEW ENGLAND"],
            "NE")
        self.assertEqual(
            n.TEAM_NAME["NEW ORLEANS"],
            "NO")
        self.assertEqual(
            n.TEAM_NAME["NY GIANTS"],
            "NYG")
        self.assertEqual(
            n.TEAM_NAME["NY JETS"],
            "NYJ")
        self.assertEqual(
            n.TEAM_NAME["OAKLAND"],
            "OAK")
        self.assertEqual(
            n.TEAM_NAME["PHILADELPHIA"],
            "PHI")
        self.assertEqual(
            n.TEAM_NAME["PITTSBURGH"],
            "PIT")
        self.assertEqual(
            n.TEAM_NAME["SAN DIEGO"],
            "SD")
        self.assertEqual(
            n.TEAM_NAME["SAN FRANCISCO"],
            "SF")
        self.assertEqual(
            n.TEAM_NAME["SEATTLE"],
            "SEA")
        self.assertEqual(
            n.TEAM_NAME["ST. LOUIS"],
            "STL")
        self.assertEqual(
            n.TEAM_NAME["TAMPA BAY"],
            "TB")
        self.assertEqual(
            n.TEAM_NAME["TENNESSEE"],
            "TEN")
        self.assertEqual(
            n.TEAM_NAME["WASHINGTON"],
            "WAS")
        self.assertEqual(
            n.TOTAL_TEAMS,
            32)
        self.assertEqual(
            n.WEEKS_IN_REG,
            17)
        self.assertEqual(
            n.YEAR,
            2013)
        self.assertEqual(
            n.WEEK_ONE[n.YEAR],
            datetime.datetime(2013, 9, 3, 9, 0, 0))
        self.assertEqual(
            n.WEEK_PREFIX['PRE'], 
            100, 
            'Prefix value for pre-season games')
        self.assertEqual(
            n.WEEK_PREFIX['REG'], 
            200,
            'Prefix value for regular season games')
        self.assertEqual(
            n.WEEK_PREFIX['POS'],
            300,
            'Prefix value for post-season games')
        self.assertEqual(
            n.DEFAULT_WEEK,
            0,
            'Default week')

class TestParamTypes(unittest.TestCase):
    def test_score_param_types(self):
        self.assertEqual(
            pt.score["away_name"],
            "string")
        self.assertEqual(
            pt.score["away_score"],
            "int")
        self.assertEqual(
            pt.score["game_clock"],
            "string")
        self.assertEqual(
            pt.score["game_day"],
            "string")
        self.assertEqual(
            pt.score["year"],
            "int")
        self.assertEqual(
            pt.score["game_status"],
            "string")
        self.assertEqual(
            pt.score["game_tag"],
            "string")
        self.assertEqual(
            pt.score["game_time"],
            "string")
        self.assertEqual(
            pt.score["week"],
            "int")
        self.assertEqual(
            pt.score["home_name"],
            "string")
        self.assertEqual(
            pt.score["home_score"],
            "int")
        self.assertEqual(
            pt.score["spread_margin"],
            "float")
        self.assertEqual(
            pt.score["spread_odds"],
            "float")

    def test_spread_param_types(self):
        self.assertEqual(
            pt.spread["year"],
            "int")
        self.assertEqual(
            pt.spread["week"],
            "int")
        self.assertEqual(
            pt.spread["misc_picks"],
            "list")
        self.assertEqual(
            pt.spread["misc_stats"],
            "list")
        self.assertEqual(
            pt.spread["game_id"],
            "list")
        self.assertEqual(
            pt.spread["spread_margin"],
            "list")
        self.assertEqual(
            pt.spread["spread_odds"],
            "list")
        self.assertEqual(
            pt.spread["spread_winner"],
            "list")
        self.assertEqual(
            pt.spread["spread_owner"],
            "string")


class TestScoreboard(unittest.TestCase):
    def test_scoreboard(self):
        self.assertEqual(
            sb.SCOREBOARD_DATA,
            "ss")
        self.assertEqual(
            sb.GAME_PADDING,
            0)
        self.assertEqual(
            sb.REG_AWAY_NAME,
            4)
        self.assertEqual(
            sb.REG_AWAY_SCORE,
            5)
        self.assertEqual(
            sb.REG_GAME_CLOCK,
            3)
        self.assertEqual(
            sb.REG_GAME_DAY,
            0)
        self.assertEqual(
            sb.REG_GAME_SEASON,
            13)
        self.assertEqual(
            sb.REG_GAME_STATUS,
            2)
        self.assertEqual(
            sb.REG_GAME_TAG,
            12)
        self.assertEqual(
            sb.REG_GAME_TIME,
            1)
        self.assertEqual(
            sb.REG_HOME_NAME,
            6)
        self.assertEqual(
            sb.REG_HOME_SCORE,
            7)
        self.assertEqual(
            sb.REG_NFL_GAME_ID,
            10)
        self.assertEqual(
            sb.POST_AWAY_NAME,
            5)
        self.assertEqual(
            sb.POST_AWAY_NAME_FULL,
            4)
        self.assertEqual(
            sb.POST_AWAY_SCORE,
            6)
        self.assertEqual(
            sb.POST_DOWN,
            11)
        self.assertEqual(
            sb.POST_GAME_CLOCK,
            3)
        self.assertEqual(
            sb.POST_GAME_DAY,
            0)
        self.assertEqual(
            sb.POST_GAME_SEASON,
            16)
        self.assertEqual(
            sb.POST_GAME_STATUS,
            2)
        self.assertEqual(
            sb.POST_GAME_TAG,
            15)
        self.assertEqual(
            sb.POST_GAME_TIME,
            1)
        self.assertEqual(
            sb.POST_HOME_NAME,
            8)
        self.assertEqual(
            sb.POST_HOME_NAME_FULL,
            7)
        self.assertEqual(
            sb.POST_HOME_SCORE,
            9)
        self.assertEqual(
            sb.POST_NFL_GAME_ID,
            12)
        self.assertEqual(
            sb.POST_POSSESSION,
            10)
        self.assertEqual(
            sb.POST_TV_NETWORK,
            14)
        self.assertEqual(
            sb.URL_REG,
            "http://www.nfl.com/liveupdate/scorestrip/scorestrip.json")
        self.assertEqual(
            sb.URL_POST,
            "http://www.nfl.com/liveupdate/scorestrip/postseason/scorestrip.json")


class TestSpreadDataBlob(unittest.TestCase):
    def test_data_blob(self):
        self.assertEqual(
            sd.MISC_PICKS,
            "misc_picks")
        self.assertEqual(
            sd.MISC_STATS,
            "misc_stats")
        self.assertEqual(
            sd.SPREAD_OWNER,
            "owner")
        self.assertEqual(
            sd.SPREAD_WINNER,
            "spread_winner")

