from __future__ import unicode_literals

import datetime

from lib.constants import NFL as nfl

from models.spread import SpreadFactory
from models.score import ScoreFactory

from google.appengine.ext import db

class TallyModel(db.Model):
    year = db.IntegerProperty(default=999)
    week = db.IntegerProperty(required=True, default=999)
    owner = db.StringProperty(required=True, default="Nobody")
    score = db.IntegerProperty(default=0)

class _TallyDatastore():
    def save(self, week, data):
        counter = 0
        saved = False
        query = self.__query(week)

        for (index, item) in reversed(list(enumerate(data))):
            if query != None:
                for tally_data in query:
                    # Perform Update
                    if tally_data.owner == item['owner']:
                        tally_data.year = item['year'] if 'year' in item else tally_data.year
                        tally_data.week = item['week'] if 'week' in item else tally_data.week
                        tally_data.score = item['score'] if 'score' in item else tally_data.score

                        tally_data.put()
                        counter += 1
                        saved = True

            # Fresh save
            if not saved:
                TallyModel(**item).put()
                counter += 1
                saved = True

            saved = False

        return counter

    def fetch(self, week):
        query = self.__query(week)
        result = []

        for item in query:
            result.append({
                'year': item.year,
                'week': item.week,
                'owner': item.owner,
                'score': item.score
            })

        return result

    def __query(self, week):
        result = TallyModel.all().filter("week =", week)

        return result

class TallyCalculator():
    
    def count(self, week=0):
        tally = _TallyDatastore()
        scores = ScoreFactory().get_instance(depth=4)
        spreads = SpreadFactory().get_instance()
        result = []

        if week == None or week == 0:
            week = self._default_week()

        score_data = scores.fetch(week)
        spreads_data = spreads.fetch(week)

        for player in spreads_data:
            points = 0

            for game in score_data:
                game_id = unicode(game['game_id'])
                # Don't receive points for non-participating games
                if game_id not in player:
                    continue

                # Calculate spread
                score_diff = game['home_score'] - game['away_score'] + game['spread_odds']
                if game['home_name'] == player[game_id][0] and score_diff > 0:
                    points += 1
                elif game['away_name'] == player[game_id][0] and score_diff < 0:
                    points += 1

                if len(player[game_id]) > 1:
                    # Calculate Over/Under
                    total_score = game['home_score'] + game['away_score']
                    weighted_score = total_score - game['spread_margin']
                    if weighted_score > 0 and player[game_id][1][0] == 'O':
                        points += 1
                    elif weighted_score < 0 and player[game_id][1][0] == 'U':
                        points += 1

                    if len(player[game_id]) > 2:
                        player_total = int(player[game_id][2])
                        # Calculate Total Score
                        if total_score == player_total:
                            points += 1

                        difference = total_score - player_total
                        if difference <= 3 and difference >= -3:
                            points += 1

            tally_up = {
                'year': player['year'],
                'week': player['week'],
                'owner': player['owner'],
                'score': points
            } 

            result.append(tally_up)
            tally.save(week, [tally_up])

        return result


    def _default_week(self):
        time_delta = datetime.datetime.now() - nfl.WEEK_ONE[nfl.YEAR]
        current_week = (time_delta.days/7)+1

        if current_week <= 0:
            # Preseason
            time_delta = datetime.datetime.now() - nfl.PRE_WEEK_ONE[nfl.YEAR]
            current_week = (time_delta.days/7)+1
        elif current_week > 17:
            current_week = current_week
        else:
            current_week = current_week

        return current_week
