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

        self.assertEqual(response.status_code, 200, "Status code 200 OK")
        self.assertEqual(response.headers["Content-Type"], "application/json", "content type is JSON")
        self.assertEqual(response.headers["Access-Control-Allow-Origin"], "*", "Allowed access control is all")

        body = json.loads(response.body)
        self.assertEqual(body, {"status":"OK"})