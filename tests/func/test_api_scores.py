#!/usr/bin/env python
from __future__ import unicode_literals

import datetime
import json
import unittest
import webapp2

import main
from models.score import ScoreModel

from lib.constants import DATA_BLOB as d
from lib.constants import HTTP_CODE as http_code
from lib.constants import NFL as nfl
from lib.constants import SCOREBOARD as sb

from google.appengine.api import memcache
from google.appengine.ext import testbed

from test_lib.mock_service import UrlFetchMock

class TestApiScores(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_urlfetch_stub()
        # Create the mocked service & inject it into the testbed
        self.fetch_mock = UrlFetchMock()
        self.testbed._register_stub(testbed.URLFETCH_SERVICE_NAME, self.fetch_mock)

        self.app = main.get_app()
        # Define the endpoint for all our requests
        self.endpoint = "/scores"
        # Define the base request
        self.request = webapp2.Request.blank(self.endpoint)
        # Timestamp in seconds
        self.timestamp = int(datetime.datetime.now().strftime('%s'))
        # An arbitrary and unrealistic week number
        self.week = (self.timestamp % 1000) + 500
        # Content for GET requests
        self.content_str = (
            '{"ss":[["Sat","4:30","final overtime",0,"BAL",'
            '"38","DEN","35",0,0,"55829",0,"REG11","2012"'
            ']]}').encode("UTF-8")
        # Data for GET requests
        self.data = {
            "content": self.content_str,
            "final_url": (sb.URL_REG).encode("UTF-8"),
            "status_code": 200
        }
        self.fetch_mock.set_return_values(**self.data)

    def tearDown(self):
        self.testbed.deactivate()

    def test_get_basic(self):
        """
        Call GET without any arguments to test for default behavior
        """
        response = self.request.get_response(self.app)

        self.assertEqual(
            response.status_int,
            http_code.OK,
            "Status code 200 OK")
        self.assertEqual(
            response.headers['Content-Type'],
            "application/json",
            "Content-Type is \"application/json\"")

    def test_get_detect_week_parameter(self):
        """
        Call GET with the week parameter to specify the week to get.

        The Datastore will be prepopulated with data to validate against.
        """
        self.request.query_string = "week=" + str(self.week)
        self.request = webapp2.Request.blank(
            self.endpoint + "?week=" + str(self.week)
            )
        response = None
        result = []

        self.assertTrue(
            ScoreModel(
                week = self.week,
                game_id = self.timestamp
                ).put(),
            "Saving to datastore")
        self.assertEqual(
            len(ScoreModel().all().fetch(2)),
            1,
            "Datastore has exactly 1 entry")

        response = self.request.get_response(self.app)

        self.assertEqual(
            response.status_int,
            http_code.OK,
            "Status code 200 OK")
        self.assertNotEqual(
            len(response.body),
            0,
            "Response came back non-empty")

        result = json.loads(response.body)
        self.assertIsNotNone(
            result,
            "JSON loaded properly")
        self.assertEqual(
            len(result),
            1,
            "Response came back with exactly 1 entry")
        self.assertEqual(
            result[0]['week'],
            self.week,
            "Season week number is correct")
        self.assertEqual(
            result[0][d.NFL_GAME_ID],
            self.timestamp,
            "NFL game ID matches")

    @unittest.skip("Defaults are dynamic. Need to learn how to test dynamic elements")
    def test_get_catch_non_integer_for_week_param(self):
        """
        Handle the case where the parameter for 'week' isn't an expected
        integer.

        We expect behavior to default the week number and continue as
        normal.
        """
        default_week = 0
        self.request = webapp2.Request.blank(self.endpoint + "?week=" + "MaunaLoa")
        response = None
        result = []

        self.assertTrue(
            ScoreModel(
                week = default_week,
                game_id = self.timestamp
                ).put(),
            "Saving to datastore")
        self.assertEqual(
            len(ScoreModel().all().fetch(2)),
            1,
            "Datastore has exactly 1 entry")

        response = self.request.get_response(self.app)

        self.assertEqual(
            response.status_int,
            http_code.OK,
            "Status code 200 OK")
        self.assertNotEqual(
            len(response.body),
            0,
            "Response came back non-empty")

        result = json.loads(response.body)
        self.assertEqual(
            len(result),
            1,
            "Response came back with exactly 1 entry")
        # This assert needs to be updated
        self.assertEqual(
            result[0]['week'],
            default_week,
            "Season week number is correct")
        self.assertEqual(
            result[0][d.NFL_GAME_ID],
            self.timestamp,
            "NFL game ID matches")


    def test_post_basic(self):
        """
        Call POST with no parameters to test for default behavior
        """
        self.request.method = "POST"

        response = self.request.get_response(self.app)
        self.assertEqual(
            response.status_int,
            http_code.CREATED,
            "Status code 201 Created")
        self.assertEqual(
            response.headers['Content-Type'],
            "application/json",
            "Content-Type is \"application/json\"")

    def test_post_single_game(self):
        """
        Call POST with enough parameters for a single game to test for
        result.

        Need to validate the datastore & memcache layers
        """
        self.request.method = "POST"
        self.request.POST[d.GAME_WEEK] = self.week
        self.request.POST[d.NFL_GAME_ID] = self.timestamp
        response = None
        query = None
        tag = "SCORES_S" + unicode(nfl.YEAR) + "W" + unicode(self.week)

        query = ScoreModel().all().fetch(2)
        self.assertEqual(
            len(query),
            0,
            "Datastore is empty")

        response = self.request.get_response(self.app)
        self.assertEqual(
            response.status_int,
            http_code.CREATED,
            "Status code 201 Created")

        # Validate datastore
        query = ScoreModel().all().fetch(2)
        self.assertEqual(
            len(query),
            1,
            "Datastore has exactly 1 entry")
        self.assertEqual(
            query[0].week,
            self.week,
            "Season week number is correct")
        self.assertEqual(
            query[0].game_id,
            self.timestamp,
            "NFL game ID matches")

        # Validate memcache
        query = memcache.get(tag)
        self.assertIsNotNone(
            query,
            "Memcache hit")
        query = json.loads(query)
        self.assertEqual(
            query['data'][0]['week'],
            self.week,
            "Season week number is correct")
        self.assertEqual(
            query['data'][0][d.NFL_GAME_ID],
            self.timestamp,
            "NFL game ID matches")

    def test_post_with_incorrect_parameter(self):
        """
        Call POST with an incorrect parameter.
        """
        self.request.method = "POST"
        self.request.POST[d.GAME_WEEK] = self.week
        self.request.POST[d.NFL_GAME_ID] = self.timestamp
        self.request.POST["gameid"] = self.timestamp + 1

        response = None
        query = None
        tag = "SCORES_S" + unicode(nfl.YEAR) + "W" + unicode(self.week)

        query = ScoreModel().all().fetch(2)
        self.assertEqual(
            len(query),
            0,
            "Datastore is empty")

        response = self.request.get_response(self.app)
        self.assertEqual(
            response.status_int,
            http_code.CREATED,
            "Status code 201 Created")

        # Validate datastore
        query = ScoreModel().all().fetch(2)
        self.assertEqual(
            len(query),
            1,
            "Datastore has exactly 1 entry")
        self.assertEqual(
            query[0].week,
            self.week,
            "Season week number is correct")
        self.assertEqual(
            query[0].game_id,
            self.timestamp,
            "NFL game ID matches")

        # Validate memcache
        query = memcache.get(tag)
        self.assertIsNotNone(
            query,
            "Memcache hit")
        query = json.loads(query)
        self.assertEqual(
            query['data'][0]['week'],
            self.week,
            "Season week number is correct")
        self.assertFalse(
            "gameid" in query['data'][0],
            "Fake NFL game ID is missing")

    def test_all_data_propogates_from_source_to_mecache(self):
        """
        Handle the case where the score source doesn't have data but
        the datastore does (i.e., spread data), and have it propogate
        to memcache.
        """
        self.request = webapp2.Request.blank(self.endpoint)
        response = None
        result = []
        # 55829 is from test content_str
        expected_game_id = 55829
        # 11 is from test content_str, 200 is regular season prefix
        expected_week = 211
        additional_data = {
            "week": expected_week,
            "game_id": expected_game_id,
            "spread_odds": -7.5,
            "spread_margin": 48.5
        }

        self.assertTrue(
            ScoreModel(**additional_data).put(),
            "Saving to datastore")
        self.assertEqual(
            len(ScoreModel().all().fetch(2)),
            1,
            "Datastore has exactly 1 entry")

        response = self.request.get_response(self.app)

        self.assertEqual(
            response.status_int,
            http_code.OK,
            "Status code 200 OK")
        self.assertNotEqual(
            len(response.body),
            0,
            "Response came back non-empty")

        result = json.loads(response.body)
        self.assertEqual(
            len(result),
            1,
            "Response came back with exactly 1 entry")

        for key in additional_data:
            target = result[0]
            self.assertTrue(
                key in target,
                'Data has key for ' + key)

            self.assertEqual(
                additional_data[key],
                target[key],
                'Data for key "' + key + '" is correct')

    def test_options_basic(self):
        origin = 'http://spread.hellaballer.com'
        request_method = 'POST'
        request_header = 'Content-Type'

        self.request.method = "OPTIONS"
        self.request.headers['Origin'] = origin
        self.request.headers['Access-Control-Request-Method'] = request_method
        self.request.headers['Access-Control-Request-Headers'] = request_header
        response = None

        response = self.request.get_response(self.app)

        self.assertEqual(
            origin,
            response.headers['Access-Control-Allow-Origin'])
        self.assertTrue(
            request_method in response.headers['Access-Control-Allow-Methods'])
        self.assertEqual(
            request_header,
            response.headers['Access-Control-Allow-Headers'])
        self.assertEqual(
            'application/json; charset=utf-8',
            response.headers['Content-Type'])

    def test_week_id_slug(self):
        self.request = webapp2.Request.blank(
            self.endpoint + '/' + str(self.week)
            )
        response = None
        result = []

        self.assertTrue(
            ScoreModel(
                week = self.week,
                game_id = self.timestamp
                ).put(),
            "Saving to datastore")
        self.assertEqual(
            len(ScoreModel().all().fetch(2)),
            1,
            "Datastore has exactly 1 entry")

        response = self.request.get_response(self.app)

        self.assertEqual(
            response.status_int,
            http_code.OK,
            "Status code 200 OK")
        self.assertNotEqual(
            len(response.body),
            0,
            "Response came back non-empty")

        result = json.loads(response.body)
        self.assertIsNotNone(
            result,
            "JSON loaded properly")
        self.assertEqual(
            len(result),
            1,
            "Response came back with exactly 1 entry")
        self.assertEqual(
            result[0]['week'],
            self.week,
            "Season week number is correct")
        self.assertEqual(
            result[0][d.NFL_GAME_ID],
            self.timestamp,
            "NFL game ID matches")
        
