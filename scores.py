#! /usr/bin/env python
from __future__ import unicode_literals

try: import simplejson as json
except ImportError: import json
import datetime
import logging
import webapp2

from lib.constants import CONSTANTS as c
from lib.constants import DATA_BLOB as d
from lib.constants import HTTP_CODE as http_code
from lib.constants import NFL as nfl
from lib.constants import PARAM_TYPES as pt
from lib.utils import Utils as utils

from google.appengine.ext.webapp.util import run_wsgi_app
from models.score import ScoreFactory

class MainPage(webapp2.RequestHandler):
    DEBUG = False

    def get(self, week_id=0):
        data = {}
        result = []
        score = ScoreFactory().get_instance()

        week_req = week_id or self.request.get(
            d.GAME_WEEK, 
            default_value=utils.default_week())
        week = (self._validate_params(d.GAME_WEEK, week_req) or
                utils.default_week())

        result = score.fetch(week)

        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.set_status(http_code.OK)
        self.response.out.write(json.dumps(result, indent = 4))

    def options(self):
        self.response.headers['Access-Control-Allow-Origin'] = 'http://spread.hellaballer.com'
        self.response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT'
        self.response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        self.response.set_status(http_code.OK)

    def post(self):
        data = {}
        result = {
            "data": 0,
            "Success": "Success",
            "status_code": 201
            }
        score = ScoreFactory().get_instance()
        week = utils.default_week()

        parameters = self.request.POST.items()
        for item in parameters:
            value = self._validate_params(item[0], item[1])
            if value != None:
                data[item[0]] = value

        if d.NFL_GAME_ID in data:
            if d.GAME_WEEK in data:
                week = data[d.GAME_WEEK]
        
            result['data'] = score.save(week, [data])

        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.set_status(result['status_code'])
        self.response.out.write(json.dumps(result, indent = 4))

    def _validate_params(self, key, value):
        conversion_key = pt.score.get(key.lower(), "")

        try:
            if isinstance(value, basestring):
                if not isinstance(value, unicode):
                    value = unicode(value, c.ENCODING)

            function = {
                "int": int,
                "float": float,
                "list": None,
                "string": None,
                "": None
            } [conversion_key]

            return value if function is None else function(value)
        except ValueError:
            logging.error("Cannot convert value " + unicode(value))

        # Default values based on conversion type
        return {
            "int": 0,
            "float": 0.0,
            "list": [],
            "string": "",
            "": None
        } [conversion_key]
        

app = webapp2.WSGIApplication(
    [
        ('/scores', MainPage),
        ('/scores/(.*)', MainPage)
    ],
    debug=True)


def main():
    run_wsgi_app(app)

if __name__ == "__main__":
    main()