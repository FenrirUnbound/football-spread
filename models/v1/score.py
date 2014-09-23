from google.appengine.ext import ndb

class _ScoreModel(ndb.Model):
    away = ndb.StringProperty()
    game_id = ndb.IntegerProperty(required=True)
    home = ndb.StringProperty()
    week = ndb.IntegerProperty(required=True)
    year = ndb.IntegerProperty(required=True)

class Score(object):
    def __init__(self, nextScore=None):
        self.next = nextScore

    def get(self, year, week):
        key = self.generate_key(year, week)
        query = _ScoreModel.query(ancestor=key)

        # Change query max
        return query.fetch(25)

    def generate_key(self, year, week):
        return ndb.Key('year', year, 'week', week)
