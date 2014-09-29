from __future__ import unicode_literals

import random
from models.v1.score import _ScoreModel as ScoreModel


from google.appengine.ext import ndb

class TestGameFactory(object):
    def generate_data(self, year=1999, week=0):
        parent_key = ndb.Key('year', year, 'week', week)

        return ScoreModel(
            parent=parent_key,
            week=week,
            year=year,
            game_id=self.__random_game_id()
            )

    def __random_game_id(self):
        return random.randint(1000, 3000)