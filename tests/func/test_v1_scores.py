from __future__ import unicode_literals


import json
import main_v1 as main
from test_lib.test_game_factory import TestGameFactory
from test_lib.utils import TestRequest
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
        self.request = TestRequest()

    def tearDown(self):
        self.testbed.deactivate()

    def test_specific_year_and_week(self):
        """
        GET the group of game scores of a specific year and week
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

        body = self.request.get_request("/api/v1/scores/year/" + unicode(test_year) + "/week/" + unicode(test_week))
        self.assertEqual(len(body), 1, "Response has 1 element: " + unicode(len(body)))

        check = body[0]
        self.assertEqual(check, test_data[0].to_dict())

