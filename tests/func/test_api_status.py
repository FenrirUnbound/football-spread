from __future__ import unicode_literals

import json
import main_v1 as main
import unittest
import webapp2

class TestApiStatus(unittest.TestCase):
    def test_status(self):
        """
        GET the api status, which should be OK.
        """
        request = webapp2.Request.blank("/api/v1/status")
        response = request.get_response(main.application)
        body = ""

        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.headers["Access-Control-Allow-Origin"], "*")

        body = json.loads(response.body)
        self.assertEqual(body, {"status":"OK"})