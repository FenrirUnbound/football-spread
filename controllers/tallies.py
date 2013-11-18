#! /usr/bin/env python
from __future__ import unicode_literals

try: import simplejson as json
except ImportError: import json
import datetime
import logging
import webapp2

from google.appengine.ext.webapp.util import run_wsgi_app

from lib.constants import CONSTANTS as c
from lib.constants import DATA_BLOB as d
from lib.constants import HTTP_CODE as http_code
from lib.constants import NFL as nfl
from lib.constants import PARAM_TYPES as pt

from models.tally import TallyCalculator

class MainPage(webapp2.RequestHandler):
    def get(self):
        tally = TallyCalculator()
        result = {}

        week_req = self.request.get(
            d.GAME_WEEK, 
            default_value=self._default_week())
        week = (self._validate_params(d.GAME_WEEK, week_req) or
                self._default_week())

        result = tally.count(week)

        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.set_status(http_code.OK)
        self.response.out.write(json.dumps(result, indent = 4))

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
        

app = webapp2.WSGIApplication([('/helper/tally', MainPage)],
                              debug=True)


def main():
    run_wsgi_app(app)

if __name__ == "__main__":
    main()