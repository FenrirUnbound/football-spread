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
from lib.utils import Utils as utils

from models.spread import SpreadFactory

class MainPage(webapp2.RequestHandler):
    def get(self):
        spread = SpreadFactory().get_instance()
        result = {}

        week_req = self.request.get(
            d.GAME_WEEK, 
            default_value=utils.default_week())
        week = (self._validate_params(d.GAME_WEEK, week_req) or
                utils.default_week())

        result = spread.fetch(week)

        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.set_status(http_code.OK)
        self.response.out.write(json.dumps(result, indent = 4))

    def post(self):
        spread = SpreadFactory().get_instance()
        data = {}
        result = {
            "data": 0,
            "Success": "Success",
            "status_code": http_code.CREATED
        }
        week = utils.default_week()
        values = []
        key = ''


        for item in self.request.POST.items():
            values = self.request.POST.getall(item[0])
            key = item[0]

            # Keys should only be strings
            if not isinstance(item[0], basestring):
                try:
                    key = unicode(item[0])
                except ValueError:
                    logging.error("Cannot convert key. Skipping")
                    continue

            # Trim endings off keys for array objects
            if key[-2:] == '[]':
                key = self._trim_keys(key)
                value = values
            else:
                # Can only validate non-list items
                value = self._validate_params(key, values.pop())

            data[key] = value

        if d.GAME_WEEK in data:
            week = data[d.GAME_WEEK]

        result["data"] = spread.save(week, [data])

        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.set_status(result["status_code"])
        self.response.out.write(json.dumps(result["data"], indent = 4))

    def _validate_params(self, key, value):
        conversion_key = pt.spread.get(key.lower(), "")

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


    def _trim_keys(self, key):
        return key[:-2]
        

app = webapp2.WSGIApplication([('/spreads', MainPage)],
                              debug=True)


def main():
    run_wsgi_app(app)

if __name__ == "__main__":
    main()