from __future__ import unicode_literals

import json
import main_v1 as main
from unittest import TestCase
import webapp2

class TestRequest(object):
    def __init__(self):
        # 'setUp' is chosen to appease constructor; it does nothing except get us asserts
        self.test = TestCase(methodName='setUp')

    def get_request(self, endpoint):
        """
        Perform a HTTP GET request against a given endpoint in the application
        """
        request = webapp2.Request.blank(endpoint)
        response = request.get_response(main.application)

        self.test.assertEqual(response.status_code, 200)
        self.test.assertEqual(response.headers["Content-Type"], "application/json")
        self.test.assertEqual(response.headers["Access-Control-Allow-Origin"], "*")

        return json.loads(response.body)