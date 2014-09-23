from __future__ import unicode_literals

import json
import webapp2

from models.v1.score import Score

class WeeklyScores(webapp2.RequestHandler):
    def get(self, year, week):
        score = Score()
        year = int(year)
        week = int(week)

        result = score.get(year, week)
        stuff = []

        for item in result:
            stuff.append(item.to_dict())

        result = stuff

        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.write(json.dumps(result, indent = 4))