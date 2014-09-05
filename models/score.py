from __future__ import unicode_literals

import datetime
try: import simplejson as json
except ImportError: import json

from lib.constants import DATA_BLOB as d
from lib.constants import HTTP_CODE as http_code
from lib.constants import NFL as nfl
from lib.constants import SCOREBOARD as sb
from lib.utils import Utils as utils

from models.format_scores import FormatFactory

from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import urlfetch

class ScoreModel(db.Model):
    year = db.IntegerProperty(required=True, default=999)
    week = db.IntegerProperty(required=True, default=999)
    away_name = db.StringProperty(default="")
    away_score = db.IntegerProperty(default=0)
    home_name = db.StringProperty(default="")
    home_score = db.IntegerProperty(default=0)
    game_clock = db.StringProperty(default="00:00")
    game_day = db.StringProperty(default="Sun")
    game_status = db.StringProperty(default="")
    game_tag = db.StringProperty(default="")
    game_time = db.StringProperty(default="00:00")
    game_id = db.IntegerProperty(required=True, default=0)
    spread_odds = db.FloatProperty(default=0.000)
    spread_margin = db.FloatProperty(default=0.000)
    timestamp = db.DateTimeProperty(auto_now=True)

class ScoreFactory():
    def get_instance(self, depth=4):
        instance = self.__create_instance(depth)

        return instance

    def __create_instance(self, depth=4):
        if depth == 0:
            return None
        elif depth == 1:
            return _ScoreMemcache(None)
        elif depth == 2:
            return _ScoreMemcache(_ScoreDatastore(None))
        elif depth == 3:
            return _ScoreMemcache(_ScoreDatastore(_ScoreSource(None)))

        return _ScoreFilter(_ScoreMemcache(_ScoreDatastore(_ScoreSource(None))))

class Score(object):
    def __init__(self, nextScore=None):
        self.next = nextScore

    def fetch(self, week):
        result = self._fetch_score(week)

        if result != None and len(result) > 0:
            return result
        elif self.next != None:
            result = self.next.fetch(week)

            # Save the result
            self._save_score(week, result)

            return result

        return None

    def save(self, week, data):
        result = 0
        result_of_next = 0
        if self.next != None:
            result_of_next = self.next.save(week, data)

        result = self._save_score(week, data)

        # TODO compare result_of_next & result for disparity

        return result

    def _fetch_score(self, week):
        raise NotImplementedError("Subclasses should implement this")

    def _save_score(self, week, data):
        raise NotImplementedError("Subclasses should implement this")


class _ScoreMemcache(Score):
    __PREFIX = "SCORES_"
    __THRESHOLD = 300   # 5 minutes in seconds

    def __init__(self, nextScore=None):
        super(_ScoreMemcache, self).__init__(nextScore=nextScore)

    def _fetch_score(self, week):
        data = {}
        tag = self.__tag(week)
        query = None

        query = memcache.get(tag)
        if query != None:
            if len(query) > 0:
                data = json.loads(query)
                now = self.__timestamp()

                # Check if data is fresh enough to be valid
                if (now - data['timestamp']) < _ScoreMemcache.__THRESHOLD:
                    return data['data']
            elif len(query) == 0:
                # Kick data out of memcache if it exists, but is empty
                memcache.delete(tag)

        return None

    def _save_score(self, week, input_data):
        data = self.__validate_data(input_data)
        scores = self.__sync_with_scores(week, data)
        save = {
            "timestamp": self.__timestamp(),
            "data": scores
        }
        tag = self.__tag(week)
        status = False
        valid_keys = []

        status = memcache.set(
            tag,
            json.dumps(save, ensure_ascii=False),
            _ScoreMemcache.__THRESHOLD)

        if status:
            # Differeniate lengths of lists vs dicts
            if type(data) is list:
                return len(data)
            else:
                return 1

        return 0

    def __sync_with_scores(self, week, input_data):
        result = []

        result = self._fetch_score(week)

        if result is None or len(result) == 0:
            result = input_data
        else:
            # Find the matching game(s)
            for data in input_data:
                for game in result:
                    if game[d.NFL_GAME_ID] == data[d.NFL_GAME_ID]:
                        # TODO too complicated/fancy
                        keys = (
                            val for name, val in vars(d).iteritems()
                            if not name.startswith("__"))
                        for key in keys:
                            # Only use the key if one of the sets contains it
                            if key in game or key in data:
                                game[key] = data[key] if key in data else game[key]

        return result

    def __tag(self, week):
        current_season = "S" + unicode(nfl.YEAR)
        current_week = "W"

        if week < 10:
            current_week += "0" + unicode(week)
        else:
            current_week += unicode(week)

        return _ScoreMemcache.__PREFIX + current_season + current_week

    def __timestamp(self):
        return int(datetime.datetime.now().strftime('%s'))

    def __validate_data(self, data):
        game = {}
        result = []
        valid_keys = []

        # Accumulate valid key
        for item in dir(d):
            if not item.startswith('_'):
                valid_keys.append(getattr(d, item))

        # Filter for & only save valid keys
        for item in data:
            for key in valid_keys:
                if key in item:
                    game[key] = item[key]

            result.append(game)
            game = {}

        return result

class _ScoreDatastore(Score):
    __THRESHOLD = 300   # 5 minutes in seconds

    def __init__(self, nextScore=None):
        super(_ScoreDatastore, self).__init__(nextScore=nextScore)

    def _fetch_score(self, week):
        stale_timestamp = (
            datetime.datetime.utcnow() -
            datetime.timedelta(seconds=_ScoreDatastore.__THRESHOLD))
        scores = []
        result = []

        scores = self.__query_scores(week)
        for game in scores:
            # Only check for staleness when dealing with current games
            if week%100 >= utils.default_week():
                # Reject data if any of it is stale
                if game.timestamp <= stale_timestamp:
                    return []

            result.append( {
                d.AWAY_NAME: game.away_name,
                d.AWAY_SCORE: game.away_score,
                d.GAME_CLOCK: game.game_clock,
                d.GAME_DAY: game.game_day,
                d.GAME_SEASON: game.year,
                d.GAME_STATUS: game.game_status,
                d.GAME_TAG: game.game_tag,
                d.GAME_TIME: game.game_time,
                d.GAME_WEEK: game.week,
                d.HOME_NAME: game.home_name,
                d.HOME_SCORE: game.home_score,
                d.NFL_GAME_ID: game.game_id,
                d.SPREAD_MARGIN: game.spread_margin,
                d.SPREAD_ODDS: game.spread_odds
            } )

        return result

    def _save_score(self, week, data):
        """
        Check the DB if there are any games of the specific week.

        If there are:
            For each game, check if we have a match in the incoming data
            list. If we do, update the game and remove from the data list.

            Any elements left in the data list will be added.

        Otherwise, add the scores.

        Note:
            Spread data should never be updated by this
        """
        counter = 0
        # Bug 118: Trust the data set over the passed-in week value
        week = data[0][d.GAME_WEEK] if (data != None and d.GAME_WEEK in data[0]) else week
        query = self.__query_scores(week)
        current_data = data
        saved = False

        if query != None:
            scores = self.__scores_to_dict(query)

            for item in data:
                game_id = item[d.NFL_GAME_ID]

                if game_id in scores:
                    game = scores[game_id]
                    updated_game = self.__merge_datasets(game, item)

                    # Propogate spread data, since datastore is Source of Truth for spread data
                    # TODO: chck if this hack is needed anymore
                    item[d.SPREAD_MARGIN] = game.spread_margin
                    item[d.SPREAD_ODDS] = game.spread_odds

                    updated_game.put()
                    counter += 1
                else:
                    # new to the data set
                    item[d.GAME_WEEK] = week
                    ScoreModel(**item).put()

                    counter += 1
        else:
            for item in data:
                item[d.GAME_WEEK] = week
                ScoreModel(**item).put()

                counter += 1

        return counter


    def __merge_datasets(self, model, data):
        """Merges a given DB Model and an equivalent dict

        Note: This does mutate model. This is to guarantee that the db object updates and does not
        create another entity/row.

        arguments:
        model -- the actual ScoreModel data
        data -- the dict equivalent of ScoreModel data
        """
        model.away_name = data[d.AWAY_NAME] if d.AWAY_NAME in data else model.away_name
        model.away_score = data[d.AWAY_SCORE] if d.AWAY_SCORE in data else model.away_score
        model.game_clock = data[d.GAME_CLOCK] if d.GAME_CLOCK in data else model.game_clock
        model.game_day = data[d.GAME_DAY] if d.GAME_DAY in data else model.game_day
        model.game_id = data[d.NFL_GAME_ID] if d.NFL_GAME_ID in data else model.game_id
        model.game_status = (data[d.GAME_STATUS] if d.GAME_STATUS in data else model.game_status)
        model.game_tag = data[d.GAME_TAG] if d.GAME_TAG in data else model.game_tag
        model.game_time = data[d.GAME_TIME] if d.GAME_TIME in data else model.game_time
        model.home_name = data[d.HOME_NAME] if d.HOME_NAME in data else model.home_name
        model.home_score = data[d.HOME_SCORE] if d.HOME_SCORE in data else model.home_score
        model.week = data[d.GAME_WEEK] if d.GAME_WEEK in data else model.week
        model.year = data[d.GAME_SEASON] if d.GAME_SEASON in data else model.year
        model.spread_margin = data[d.SPREAD_MARGIN] if d.SPREAD_MARGIN in data else model.spread_margin
        model.spread_odds = data[d.SPREAD_ODDS] if d.SPREAD_ODDS in data else model.spread_odds

        return model


    def __is_same(self, game_model, game_dict):
        if game_model.game_id == game_dict[d.NFL_GAME_ID]:
            return True
        if game_model.home_name == game_dict[d.HOME_NAME]:
            if game_model.away_name == game_dict[d.AWAY_NAME]:
                return True

        return False


    def __scores_to_dict(self, scores):
        """ Creates a list of score models into a dict, using the game_id as the key

        arguments:
        scores -- list of ScoreModel data
        """
        result = {}

        for game in scores:
            game_id = game.game_id
            result[game_id] = game

        return result

    def __query_scores(self, week):
        query = db.GqlQuery('SELECT * FROM ScoreModel ' +
                            'WHERE week = :1 ' +
                            'ORDER BY game_id DESC',
                            week)

        return query.run(limit=nfl.TOTAL_TEAMS)


class _ScoreSource(Score):
    def __init__(self, nextScore=None):
        super(_ScoreSource, self).__init__(nextScore=nextScore)

        self.formatter = FormatFactory().get_instance()

    def _fetch_score(self, week):
        return self.__fetch_scores(week)

    def __fetch_scores(self, week):
            """
            NOTE: 'week' is for checking for postseason data
            """
            is_postseason = week > nfl.WEEKS_IN_REG
            scores = {}
            result = []
            status_code = 0

            rpc = urlfetch.create_rpc()

            if is_postseason:
                urlfetch.make_fetch_call(rpc, sb.URL_POST)
            else:
                urlfetch.make_fetch_call(rpc, sb.URL_REG)

            try:
                response = rpc.get_result()

                # Check if the fetch was successful
                if response.status_code == http_code.OK:
                    result = self.formatter.format(response.content)

                # Save the status code
                status_code = response.status_code
            except urlfetch.DownloadError:
                status_code = http_code.INTERNAL_SERVER_ERROR
                logging.error("An unexpected error occurred while "
                              "fetching for ScoreSource."
                              "(" + unicode(status_code) + ")")

            # Don't save data that isn't good; just return nothing
            if status_code != http_code.OK:
                return []

            return result

    def _save_score(self, week, data):
        return len(data)


class _ScoreFilter(Score):
    def __init__(self, nextScore=None):
        super(_ScoreFilter, self).__init__(nextScore=nextScore)

    def fetch(self, week):
        """
        Override.

        This is to help namespace the week value internally
        """
        result = None

        if week < nfl.WEEK_PREFIX['PRE']:
            week += self.__week_offset()

        if self.next != None:
            result = self.next.fetch(week)

            return result

        return None

    def save(self, week, data):
        result = None

        if week < nfl.WEEK_PREFIX['PRE']:
            week += self.__week_offset()

        if self.next != None:
            result = self.next.save(week, data)

        return result

    def __week_offset(self):
        current_week = utils.default_week()

        if current_week <= 0:
            # Preseason
            return nfl.WEEK_PREFIX['PRE']
        elif current_week > 17:
            return nfl.WEEK_PREFIX['POS']
        else:
            return nfl.WEEK_PREFIX['REG']

