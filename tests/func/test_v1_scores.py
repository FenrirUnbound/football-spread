from __future__ import unicode_literals


import json
import main_v1 as main
from test_lib.test_game_factory import TestGameFactory
from models.v1.score import _ScoreModel as ScoreModel
import unittest
import webapp2


from google.appengine.ext import testbed
from google.appengine.ext import ndb

class TestScoresAPI(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_memcache_stub()
        self.testbed.init_datastore_v3_stub()
        self.data_generator = TestGameFactory()

    def tearDown(self):
        self.testbed.deactivate()

    def test_specific_year_and_week(self):
        """
        GET the latest scores
        """
        test_week = 2
        test_year = 2015
        test_data = [
            self.data_generator.generate_data(test_year, test_week),
            self.data_generator.generate_data(test_year, test_week+1)
        ]
        body = {}

        for item in test_data:
            item.put()

        request = webapp2.Request.blank("/api/v1/scores/year/" + unicode(test_year) + "/week/" + unicode(test_week))
        response = request.get_response(main.application)


        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.headers["Access-Control-Allow-Origin"], "*")

        body = json.loads(response.body)
        self.assertEqual(len(body), 1, "Response has 1 element: " + unicode(len(body)))

        check = body[0]
        self.assertEqual(check, test_data[0].to_dict())

