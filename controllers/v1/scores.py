from __future__ import unicode_literals

import json
import webapp2

from models.v1.score import Score

class WeeklyScores(webapp2.RequestHandler):
    def __init__(self, request, response):
        self.initialize(request, response)
        self.score = Score()

    def get(self, year, week):
        year = int(year)
        week = int(week)

        scores = self.score.get(year, week)
        result = []

        for item in scores:
            result.append(item.to_dict())

        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.write(json.dumps(result, indent = 4))