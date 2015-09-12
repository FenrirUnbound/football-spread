#!/usr/bin/env python

from __future__ import unicode_literals

import datetime
import json
import unittest

from lib.constants import DATA_BLOB as d
from lib.constants import SCOREBOARD as sb

from models.score import ScoreFactory
from models.score import Score
from models.score import ScoreModel

from google.appengine.api import memcache
from google.appengine.ext import testbed

from test_lib.datablob_factory import DataBlobFactory
from test_lib.mock_service import UrlFetchMock

class TestScoreFactory(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_urlfetch_stub()

        # Create the mocked service & inject it into the testbed
        self.fetch_mock = UrlFetchMock()
        self.testbed._register_stub(testbed.URLFETCH_SERVICE_NAME, self.fetch_mock)

        self.score = ScoreFactory().get_instance(depth=3)

        self.factory = DataBlobFactory()
        self.timestamp = int(datetime.datetime.now().strftime('%s'))
        self.week = self.timestamp  % 50 + 50
        self.tag = "SCORES_S2015W" + unicode(self.week)

    def tearDown(self):
        self.testbed.deactivate()

    def test_save_data(self):
        """
        Validate instance saves data to Memcache & Datastore
        """
        data = self.factory.generate_data(week=self.week)
        result = 0
        result_dict = {}
        result_str = ""

        result = self.score.save(self.week, [data])
        self.assertEqual(
            result,
            1,
            "Saved the correct amount")

        # Validate against memcache
        result_str = memcache.get(self.tag)
        self.assertIsNotNone(
            result_str,
            "Memcache miss")

        result_dict = json.loads(result_str)['data'][0]
        self.assertEqual(
            len(result_dict),
            len(data),
            "Size of data is correct")
        self.assertEqual(
            result_dict['away_score'],
            data['away_score'],
            "Away score is correct")
        self.assertEqual(
            result_dict['home_score'],
            data['home_score'],
            "Home score is correct")
        self.assertEqual(
            result_dict[d.NFL_GAME_ID],
            data[d.NFL_GAME_ID],
            "NFL game ID matches")
        self.assertEqual(
            result_dict['week'],
            self.week,
            "Season week matches")

        # Validate against datastore
        result_dict = ScoreModel().all().fetch(2)
        self.assertEqual(
            len(result_dict),
            1,
            "Fetched exactly 1 from datastore")
        self.assertEqual(
            result_dict[0].away_score,
            data['away_score'],
            "Away score is correct")
        self.assertEqual(
            result_dict[0].home_score,
            data['home_score'],
            "Home score is correct")
        self.assertEqual(
            result_dict[0].game_id,
            data[d.NFL_GAME_ID],
            "NFL game ID matches")
        self.assertEqual(
            result_dict[0].week,
            data['week'],
            "Season week matches")


    def test_fetch_memcache_data(self):
        """
        Validate that we can fetch data from memcache.
        Datastore should not be affected by this
        """
        data = self.factory.generate_data(
            timestamp=self.timestamp,
            week=self.week)
        result = None

        self.assertTrue(
            memcache.add(self.tag, json.dumps(data)),
            "Saving to memcache")

        result = self.score.fetch(self.week)
        self.assertIsNotNone(
            result,
            "Fetch success")
        self.assertEqual(
            len(result),
            len(data['data']),
            "Size of data is correct")
        self.assertEqual(
            result['away_score'],
            data['data']['away_score'],
            "Away score is correct")
        self.assertEqual(
            result['home_score'],
            data['data']['home_score'],
            "Home score is correct")
        self.assertEqual(
            result[d.NFL_GAME_ID],
            data['data'][d.NFL_GAME_ID],
            "NFL game ID matches")

        # Check that Datastore is unaffected
        result = ScoreModel().all().fetch(2)
        self.assertEqual(
            len(result),
            0,
            "Data doesn't exist in datastore")

    def test_fetch_datastore_data_and_propogate_to_memcache(self):
        """
        Validate we can fetch data from datastore, and have it propogate
        to the Memcache level.
        """
        data = self.factory.generate_data(week=self.week)
        result = None
        result_dict = {}
        result_str = ""

        self.assertTrue(
            ScoreModel(**data).put(),
            "Pushed data to datastore")

        result = self.score.fetch(self.week)
        self.assertIsNotNone(
            result,
            "Fetch success")
        self.assertEqual(
            len(result),
            1,
            "Received total number of elements expected")
        self.assertEqual(
            result[0]['away_score'],
            data['away_score'],
            "Away score is correct")
        self.assertEqual(
            result[0]['home_score'],
            data['home_score'],
            "Home score is correct")
        self.assertEqual(
            result[0][d.NFL_GAME_ID],
            data[d.NFL_GAME_ID],
            "NFL game ID matches")
        self.assertEqual(
            result[0]['week'],
            data['week'],
            "Season week matches")

        # Check memcache
        result_str = memcache.get(self.tag)
        self.assertIsNotNone(
            result,
            "Memcache hit")

        # Validate data retrieved from memcache
        result_dict = json.loads(result_str)['data'][0]
        self.assertEqual(
            result_dict['away_score'],
            data['away_score'],
            "Away score is correct")
        self.assertEqual(
            result_dict['home_score'],
            data['home_score'],
            "Home score is correct")
        self.assertEqual(
            result_dict[d.NFL_GAME_ID],
            data[d.NFL_GAME_ID],
            "NFL game ID matches")
        self.assertEqual(
            result_dict['week'],
            self.week,
            "Season week matches")

    def test_fetch_source_data_and_propogates(self):
        answer_key = {
            "away_score": 20,
            "home_score": 28,
            d.NFL_GAME_ID: 56117,
            "week": 100+self.week
        }
        content_str = (
            '{"ss":[["FRI","8:00","Final",,"OAK","20","NO","28"'
            ',,,"56117",,"PRE%s","2013"]]}') % (self.week)

        data = {
            "content": content_str.encode('UTF-8'),
            "final_url": (sb.URL_REG).encode("UTF-8"),
            "status_code": 200
        }
        self.fetch_mock.set_return_values(**data)

        result = self.score.fetch(self.week)
        self.assertIsNotNone(
            result,
            "Fetch success")
        self.assertEqual(
            len(result),
            1,
            "Received total number of elements expected")
        self.assertEqual(
            result[0]['away_score'],
            answer_key['away_score'],
            "Away score is correct")
        self.assertEqual(
            result[0]['home_score'],
            answer_key['home_score'],
            "Home score is correct")
        self.assertEqual(
            result[0][d.NFL_GAME_ID],
            answer_key[d.NFL_GAME_ID],
            "NFL game ID matches")
        self.assertEqual(
            result[0]['week'],
            answer_key['week'],
            "Season week matches")
