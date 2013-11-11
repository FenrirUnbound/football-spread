from __future__ import unicode_literals

import datetime
import json

from google.appengine.api import memcache
from google.appengine.ext import db

from lib.constants import CONSTANTS as c
from lib.constants import DATA_BLOB as d
from lib.constants import SPREAD_DATA_BLOB as sd
from lib.constants import NFL as nfl
from lib.utils import Utils as utils

class SpreadModel(db.Expando):
    year = db.IntegerProperty(required=True, default=999)
    week = db.IntegerProperty(required=True, default=999)
    owner = db.StringProperty(required=True, default="Nobody")

class SpreadFactory():
    def get_instance(self):
        return self._create_instance()

    def _create_instance(self):
        return _SpreadFilter(_SpreadMemcache(_SpreadDatastore(None)))

class Spread(object):
    def __init__(self, nextSpread=None):
        self.next = nextSpread

    def fetch(self, week):
        result = self._fetch_spread(week)

        if result != None and len(result) > 0:
            return result
        elif self.next != None:
            result = self.next.fetch(week)

            # Save the result
            self._save_spread(week, result)

            return result

        return None

    def save(self, week, data):
        result = 0
        result_of_next = 0
        if self.next != None:
            result_of_next = self.next.save(week, data)

        result = self._save_spread(week, data)

        return result

    def _fetch_spread(self, week):
        raise NotImplementedError("Subclasses should implement this")

    def _save_spread(self, week, data):
        raise NotImplementedError("Subclasses should implement this")

class _SpreadMemcache(Spread):
    __PREFIX = "SPREAD_"

    def _fetch_spread(self, week):
        data = {}
        tag = self.__tag(week)
        query = None

        query = memcache.get(tag)
        if query != None:
            if len(query) > 0:
                data = json.loads(query)
                now = self.__timestamp()
            
                # Check if data is fresh enough to be valid
                if (now - data["timestamp"]) < c.MEMCACHE_THRESHOLD:
                    if isinstance(data["data"], list):
                        return data["data"]
                    else:
                        return [data["data"]]
            elif len(query) == 0:
                # Kick data out of memcache if it exists, but is empty
                memcache.delete(tag)

        return None

    def _save_spread(self, week, data):
        save = {
            "timestamp": self.__timestamp(),
            "data": data if isinstance(data, list) else [data]
        }
        status = False

        status = memcache.set(
            self.__tag(week),
            json.dumps(save, ensure_ascii=False),
            c.MEMCACHE_THRESHOLD)

        if status:
            # Differeniate lengths of lists vs dicts
            if type(data) is list:
                return len(data)
            else:
                return 1

        return 0

    def __tag(self, week):
        current_season = "S" + unicode(nfl.YEAR)
        current_week = "W"

        if week < 10:
            current_week += "0" + unicode(week)
        else:
            current_week += unicode(week)

        return _SpreadMemcache.__PREFIX + current_season + current_week

    def __timestamp(self):
        return int(datetime.datetime.now().strftime('%s'))

class _SpreadDatastore(Spread):
    def _fetch_spread(self, week):
        query = self.__query_spread(week)
        result = []

        for entry in query:
            game = {}

            for item in entry.properties():
                game[item] = getattr(entry, item)

            for item in entry.dynamic_properties():
                game[item] = getattr(entry, item)

            result.append(game)

        return result

    def _save_spread(self, week, data):
        counter = 0
        query = self.__query_spread(week)
        current_data = data
        saved = False

        for data_item in data:
            if query != None:
                # Making an update to data instead of fresh save
                for game in query:
                    # Have to check the entire query list for a matching game
                    if self.__is_same(game, data_item):
                        for element in data_item:
                            setattr(
                                game, 
                                element, 
                                data_item[element] or getattr(game, element))

                        game.put()
                        counter += 1
                        saved = True

            if not saved:
                data_item[d.GAME_WEEK] = week
                SpreadModel(**data_item).put()

                counter += 1
                saved = True

            saved = False

        return counter

    def __query_spread(self, week):
        query = SpreadModel().all()
        query = query.filter("week = ", week).order(sd.SPREAD_OWNER)

        return query.fetch(nfl.TOTAL_TEAMS)

    def __is_same(self, spread_model, spread_dict):
        if spread_model.week == spread_dict[d.GAME_WEEK]:
            return spread_model.owner == spread_dict[sd.SPREAD_OWNER]

class _SpreadFilter(Spread):
    def __init__(self, nextSpread=None):
        self.next = nextSpread

    def fetch(self, week):
        if week < nfl.WEEK_PREFIX['PRE']:
            week += self.__week_offset()

        result = None
        if self.next != None:
            result = self.next.fetch(week)

        return result

    def save(self, week, data):
        if week < nfl.WEEK_PREFIX['PRE']:
            week += self.__week_offset()

        result = None
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
