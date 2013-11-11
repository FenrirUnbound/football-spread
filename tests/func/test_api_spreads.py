from __future__ import unicode_literals

import datetime
try: import simplejson as json
except ImportError: import json
import unittest
import webapp2

from google.appengine.api import memcache
from google.appengine.ext import testbed

from lib.constants import CONSTANTS as c
from lib.constants import HTTP_CODE as http_code
from lib.constants import NFL as nfl

from models.spread import SpreadModel

from spreads import app
from spreads import MainPage

from test_lib.datablob_factory import DataBlobFactory
from test_lib.testdata_factory import TestDataFactory

class TestApiSpreads(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        self.app = app
        self.endpoint = "/spreads"
        self.request = webapp2.Request.blank(self.endpoint)

        self.data_factory = DataBlobFactory()
        test_data = TestDataFactory()
        self.week = test_data.get_instance(data_type="week")
        self.timestamp = test_data.get_instance(data_type='timestamp')

    def tearDown(self):
        self.testbed.deactivate()

    def test_get_nothing(self):
        """
        Call GET without any arguments to test for default behavior
        """
        response = self.request.get_response(self.app)

        self.assertEqual(
            response.status_int,
            http_code.OK,
            "Status code 200 OK")
        self.assertEqual(
            response.headers["Content-Type"],
            "application/json",
            "Content-Type is \"application/json\"")

    def test_post_nothing(self):
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
            response.headers["Content-Type"],
            "application/json",
            "Content-Type is \"application/json\"")

    def test_get_specific_week(self):
        """
        Preload the datastore with 2 games with different weeks.

        Validate the correct data is returned.
        """
        data = [
            self.data_factory.generate_data(week=self.week, type="spread"),
            self.data_factory.generate_data(week=self.week+1, type="spread"),
        ]
        result_arr = []
        
        # Preload datastore
        for item in data:
            SpreadModel(**item).put()


        self.request = webapp2.Request.blank(
            (self.endpoint + "?week=" + str(self.week)).encode(c.ENCODING)
            )
        response = self.request.get_response(self.app)
        self.assertEqual(
            response.status_int,
            http_code.OK,
            "Status code 200 OK")
        self.assertNotEqual(
            len(response.body),
            0,
            "Response came back non-empty")

        result_arr = json.loads(response.body)
        self.assertIsNotNone(
            result_arr,
            "JSON loaded properly")
        self.assertEqual(
            len(result_arr),
            1,
            "Response came back with exactly 1 entry")

        for item in result_arr[0]:
            self.assertEqual(
                result_arr[0][item],
                data[0][item],
                item + " value matches")

    @unittest.skip("Defaults are dynamic. Need to learn how to test dynamic elements")
    def test_get_invalid_week(self):
        """
        Handle the case where the parameter for 'week' isn't an expected
        integer.

        We expect behavior to default the week number and continue as
        normal.
        """
        data = [
            self.data_factory.generate_data(
                week=nfl.DEFAULT_WEEK, type="spread"),
            self.data_factory.generate_data(
                week=self.week, type="spread"),
        ]
        result_arr = []
        
        # Preload datastore
        for item in data:
            SpreadModel(**item).put()

        self.request = webapp2.Request.blank(
            (self.endpoint + "?week=" + "WavyOriginal").encode(c.ENCODING))
        response = self.request.get_response(self.app)
        self.assertEqual(
            response.status_int,
            http_code.OK,
            "Status code 200 OK")
        self.assertNotEqual(
            len(response.body),
            0,
            "Response came back non-empty")

        result_arr = json.loads(response.body)
        self.assertIsNotNone(
            result_arr,
            "JSON loaded properly")
        self.assertEqual(
            len(result_arr),
            1,
            "Response came back with exactly 1 entry")

        for item in result_arr[0]:
            self.assertEqual(
                result_arr[0][item],
                data[0][item],
                item + " value matches")


    def test_post_single_entry(self):
        """
        Call POST with enough parameters for a single spread entry to test
        for result.

        Need to validate the datastore & memcache layers
        """
        data = self.data_factory.generate_data(week=self.week, type="spread")
        result = 0
        result_arr = []

        self.request.method = "POST"
        for item in data:
            self.request.POST[item] = data[item]

        # Validate that datastore is emtpy from the beginging
        result = SpreadModel().all().fetch(2)
        self.assertEqual(
            len(result), 
            0,
            "Datastore is empty")

        response = self.request.get_response(self.app)
        self.assertEqual(
            response.status_int,
            http_code.CREATED,
            "Status code 201 Created")

        # Validate datastore
        result_arr = SpreadModel().all().fetch(2)
        self.assertEqual(
            len(result_arr),
            1,
            "Exactly 1 entry in datastore")
        for entry in result_arr:
            for item in data:
                self.assertEqual(
                    getattr(entry, item),
                    data[item],
                    item + " value matches")


    def test_post_with_incorrect_parameter(self):
        """
        Call POST with an incorrect parameter.
        """
        data = self.data_factory.generate_data(week=self.week, type="spread")
        result = 0
        result_arr = []

        self.request.method = "POST"
        for item in data:
            self.request.POST[item] = data[item]

        # Incorrect parameter
        self.request.POST["Oreos"] = "YouOnlyLoveOreos"

        # Validate that datastore is emtpy from the beginging
        result = SpreadModel().all().fetch(2)
        self.assertEqual(
            len(result), 
            0,
            "Datastore is empty")

        response = self.request.get_response(self.app)
        self.assertEqual(
            response.status_int,
            http_code.CREATED,
            "Status code 201 Created")

        # Validate datastore
        result_arr = SpreadModel().all().fetch(2)
        self.assertEqual(
            len(result_arr),
            1,
            "Exactly 1 entry in datastore")
        for entry in result_arr:
            for item in data:
                self.assertEqual(
                    getattr(entry, item),
                    data[item],
                    item + " value matches")

    def test_post_with_mixed_parameter_types(self):
        data = self.data_factory.generate_data(week=self.week, type='spread')
        result = 0
        result_arr = []

        data[unicode(self.timestamp)] = ['Purple']
        data[unicode(self.timestamp+1)] = ['Seven', 8, 'Nine']
        data[unicode(self.timestamp+2)] = ['FinISH']

        self.request.method = "POST"
        for item in data:
            self.request.POST[item] = data[item]

        # Validate that datastore is emtpy from the beginging
        result = SpreadModel().all().fetch(2)
        self.assertEqual(
            len(result),
            0,
            "Datastore is empty")

        response = self.request.get_response(self.app)
        self.assertEqual(
            response.status_int,
            http_code.CREATED,
            "Status code 201 Created")

        # Validate datastore
        result_arr = SpreadModel().all().fetch(2)
        self.assertEqual(
            len(result_arr),
            1,
            "Exactly 1 entry in datastore")
        for entry in result_arr:
            for item in data:
                self.assertEqual(
                    getattr(entry, item),
                    data[item],
                    item + " value matches")

    def test_error_with_post_having_integer_as_key(self):
        data = self.data_factory.generate_data(week=self.week, type='spread')
        result = 0
        result_arr = []
        item_str = ''

        data[self.timestamp] = ['CocaCola']

        self.request.method = 'POST'
        for item in data:
            self.request.POST[item] = data[item]

        # Validate that datastore is emtpy from the beginging
        result = SpreadModel().all().fetch(2)
        self.assertEqual(
            len(result),
            0,
            "Datastore is empty")

        response = self.request.get_response(self.app)
        self.assertEqual(
            response.status_int,
            http_code.CREATED,
            "Status code 201 Created")

        # Validate datastore
        result_arr = SpreadModel().all().fetch(2)
        self.assertEqual(
            len(result_arr),
            1,
            "Exactly 1 entry in datastore")
        for entry in result_arr:
            for item in data:
                item_str = unicode(item)

                self.assertEqual(
                    getattr(entry, item_str),
                    data[item],     # Data still has integers as keys
                    item_str + " value matches")
