from google.appengine.ext import ndb

class _ScoreModel(ndb.Model):
    away_team = ndb.StringProperty()
    game_i_d = ndb.IntegerProperty(required=True)
    home_team = ndb.StringProperty()
    week = ndb.IntegerProperty(required=True)
    year = ndb.IntegerProperty(required=True)

class Score(object):
    def __init__(self, nextScore=None):
        self.next = nextScore

    def get(self, year, week):
        """
        Fetch the games of a specific year and week
        """
        key = self.generate_key(year, week)
        query = _ScoreModel.query(ancestor=key)

        # Change query max
        return query.fetch(25)

    def generate_key(self, year, week):
        """
        Generate the correct NDB entity key based on the year and week
        """
        return ndb.Key('year', year, 'week', week)
