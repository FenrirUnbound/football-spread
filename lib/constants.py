from __future__ import unicode_literals

import datetime

class CONSTANTS():
    DAYS = {
        "MON": 0,
        "TUE": 1,
        "WED": 2,
        "THU": 3,
        "FRI": 4,
        "SAT": 5,
        "SUN": 6
    }
    ENCODING = "UTF-8"
    MEMCACHE_THRESHOLD = 300

class DATA_BLOB():
    AWAY_NAME = "away_name"
    AWAY_SCORE = "away_score"
    GAME_CLOCK = "game_clock"
    GAME_DAY = "game_day"
    GAME_SEASON = "year"
    GAME_STATUS = "game_status"
    GAME_TAG = "game_tag"
    GAME_TIME = "game_time"
    GAME_WEEK = "week"
    HOME_NAME = "home_name"
    HOME_SCORE = "home_score"
    NFL_GAME_ID = "game_id"
    SPREAD_MARGIN = "spread_margin"
    SPREAD_ODDS = "spread_odds"
    TIMESTAMP = "timestamp"

class HTTP_CODE():
    OK = 200
    CREATED = 201
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500

class NFL():
    DEFAULT_WEEK = 0
    PRE_WEEK_ONE = {
        2013: datetime.datetime(2013, 8, 6, 0, 0, 0),
        2014: datetime.datetime(2014, 8, 7, 0, 0, 0),
        2015: datetime.datetime(2015, 8, 4, 0, 0, 0),
        2016: datetime.datetime(2015, 8, 9, 0, 0, 0)
    }
    TEAM_NAME = {
        "ARIZONA": "ARI",
        "ATLANTA": "ATL",
        "BALTIMORE": "BAL",
        "BUFFALO": "BUF",
        "CAROLINA": "CAR",
        "CHICAGO": "CHI",
        "CINCINNATI": "CIN",
        "CLEVELAND": "CLE",
        "DALLAS": "DAL",
        "DENVER": "DEN",
        "DETROIT": "DET",
        "GREEN BAY": "GB",
        "HOUSTON": "HOU",
        "INDIANAPOLIS": "IND",
        "JACKSONVILLE": "JAC",
        "KANSAS CITY": "KC",
        "MIAMI": "MIA",
        "MINNESOTA": "MIN",
        "NEW ENGLAND": "NE",
        "NEW ORLEANS": "NO",
        "NY GIANTS": "NYG",
        "NY JETS": "NYJ",
        "OAKLAND": "OAK",
        "PHILADELPHIA": "PHI",
        "PITTSBURGH": "PIT",
        "SAN DIEGO": "SD",
        "SAN FRANCISCO": "SF",
        "SEATTLE": "SEA",
        "ST. LOUIS": "STL",
        "TAMPA BAY": "TB",
        "TENNESSEE": "TEN",
        "WASHINGTON": "WAS"
        }
    TOTAL_TEAMS = 32
    WEEKS_IN_REG = 17
    WEEK_ONE = {
        2013: datetime.datetime(2013, 9, 3, 9, 0, 0),
        2014: datetime.datetime(2014, 9, 2, 9, 0, 0),
        2015: datetime.datetime(2015, 9, 8, 9, 0, 0),
        2016: datetime.datetime(2016, 9, 6, 9, 0, 0)
    }
    WEEK_PREFIX = {
        "PRE": 100,
        "REG": 200,
        "POS": 300,
        "PRO": 300
    }
    YEAR = 2016


class PARAM_TYPES():
    score = {
        "away_name": "string",
        "away_score": "int",
        "game_clock": "string",
        "game_day": "string",
        "game_id": "int",
        "game_status": "string",
        "game_tag": "string",
        "game_time": "string",
        "home_name": "string",
        "home_score": "int",
        "spread_margin": "float",
        "spread_odds": "float",
        "week": "int",
        "year": "int"
    }
    spread = {
        "game_id": "list",
        "misc_picks": "list",
        "misc_stats": "list",
        "spread_margin": "list",
        "spread_odds": "list",
        "spread_owner": "string",
        "spread_winner": "list",
        "week": "int",
        "year": "int"
    }

class SCOREBOARD():
    SCOREBOARD_DATA = "ss"
    GAME_PADDING = 0
    REG_AWAY_NAME = 4
    REG_AWAY_SCORE = 5
    REG_GAME_CLOCK = 3
    REG_GAME_DAY = 0
    REG_GAME_SEASON = 13
    REG_GAME_STATUS = 2
    REG_GAME_TAG = 12
    REG_GAME_TIME = 1
    REG_HOME_NAME = 6
    REG_HOME_SCORE = 7
    REG_NFL_GAME_ID = 10
    POST_AWAY_NAME = 5
    POST_AWAY_NAME_FULL = 4
    POST_AWAY_SCORE = 6
    POST_DOWN = 11
    POST_GAME_CLOCK = 3
    POST_GAME_DAY = 0
    POST_GAME_SEASON = 16
    POST_GAME_STATUS = 2
    POST_GAME_TAG = 15
    POST_GAME_TIME = 1
    POST_HOME_NAME = 8
    POST_HOME_NAME_FULL = 7
    POST_HOME_SCORE = 9
    POST_NFL_GAME_ID = 12
    POST_POSSESSION = 10
    POST_TV_NETWORK = 14
    URL_REG = "http://www.nfl.com/liveupdate/scorestrip/scorestrip.json"
    URL_POST = "http://www.nfl.com/liveupdate/scorestrip/postseason/scorestrip.json"

class SPREAD_DATA_BLOB():
    MISC_PICKS = "misc_picks"
    MISC_STATS = "misc_stats"
    SPREAD_OWNER = "owner"
    SPREAD_WINNER = "spread_winner"
