from __future__ import unicode_literals

import datetime
try: import simplejson as json
except ImportError: import json
import unittest

from google.appengine.api import memcache
from google.appengine.ext import testbed

from lib.constants import DATA_BLOB as d
from lib.constants import SPREAD_DATA_BLOB as sd
from lib.constants import NFL as nfl

from test_lib.datablob_factory import DataBlobFactory
from test_lib.testdata_factory import TestDataFactory

from models.spread import Spread
from models.spread import SpreadFactory
from models.spread import _SpreadDatastore as SpreadDatastore
from models.spread import _SpreadMemcache as SpreadMemcache
from models.spread import _SpreadFilter as SpreadFilter
from models.spread import SpreadModel


class TestSpreadModel(unittest.TestCase):
    def test_initialization(self):
        model = SpreadModel()
        test_points = {
            d.GAME_SEASON: 999,
            d.GAME_WEEK: 999,
            sd.SPREAD_OWNER: "Nobody"
        }

        self.assertIsNotNone(
            model,
            "Initialization")

        for key in test_points:
            self.assertTrue(
                hasattr(model, key),
                "Has " + key)
            self.assertEqual(
                getattr(model, key),
                test_points[key],
                "Default " + key)


class TestSpreadFactory(unittest.TestCase):
    def setUp(self):
        self.factory = SpreadFactory()

    def test_attribute_check(self):
        get_instance = self.factory.get_instance()
        create_instance = self.factory._create_instance()

        self.assertIsNotNone(
            get_instance,
            "Get instance")
        self.assertIsNotNone(
            create_instance,
            "Create instance")
        self.assertNotEqual(
            get_instance,
            create_instance,
            "Instances are different")

    def test_get_instance_is_Spread(self):
        instance = self.factory.get_instance()

        self.assertTrue(
            issubclass(instance.__class__, Spread),
            "Instance is a Spread object")
        self.assertTrue(
            hasattr(instance, "fetch"),
            "Has Fetch")
        self.assertTrue(
            hasattr(instance, "save"),
            "Has Save")

class TestSpreadMemcache(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_memcache_stub()

        self.spread_memcache = SpreadMemcache()
        self.timestamp = int(datetime.datetime.now().strftime('%s'))
        self.week = self.timestamp % 1000 + 50

    def tearDown(self):
        self.testbed.deactivate()

    def test_super_class(self):
        self.assertTrue(
            issubclass(SpreadMemcache, Spread),
            "ScoreMemcache is a subclass of Score")

    def test_missing_next_chain(self):
        self.assertIsNone(
            self.spread_memcache.next,
            "Default doesn't have next in chain")

    def test_initialization(self):
        attributes = [
            "save",
            "fetch",
        ]

        for item in attributes:
            self.assertTrue(
                hasattr(self.spread_memcache, item),
                "Has attribute " + item)

    def test_fetch_basic(self):
        """
        Fetch with nothing in memcache.

        Should expect nothing back.
        """
        result = []

        result = self.spread_memcache.fetch(self.week)
        self.assertIsNone(
            result,
            "Memcache miss")

    def test_fetch_simple(self):
        """
        Get spread data from memcache
        """
        data = DataBlobFactory().generate_data(
            timestamp=self.timestamp, type="spread")
        tag = "SPREAD_S2017W" + unicode(self.week)

        self.assertTrue(
            memcache.add(tag, json.dumps(data)),
            "Memcache add successful")

        result = self.spread_memcache.fetch(self.week)
        self.assertIsNotNone(
            result,
            "Result is not None")
        self.assertEqual(
            len(result),
            1,
            "Exactly 1 entry retrieved from memcache")

        for game in result:
            for item in game:
                self.assertEqual(
                    data["data"][item],
                    game[item],
                    unicode(item) + " is equal")

    def test_tag_creation(self):
        tag = u"SPREAD_S2017W" + unicode(self.week)

        result_str = self.spread_memcache._SpreadMemcache__tag(self.week)
        self.assertEqual(
            result_str,
            tag,
            "Tag creation")

    def test_timestamp_creation(self):
        self.assertTrue(
            self.timestamp <= self.spread_memcache._SpreadMemcache__timestamp(),
            "Timestamp creation is accurate")

    def test_save_simple(self):
        """
        Save spread data to memcache
        """
        data = DataBlobFactory().generate_data(type="spread")
        result = 0
        result_str = ""
        result_arr = []

        result = self.spread_memcache.save(self.week, data)
        self.assertEqual(
            result,
            1,
            "Saved the correct amount of data")

        result_str = memcache.get(
            self.spread_memcache._SpreadMemcache__tag(self.week))
        self.assertIsNotNone(
            result_str,
            "Memcache hit")

        result_arr = json.loads(result_str)
        self.assertEqual(
            len(result_arr["data"]),
            1,
            "Exactly 1 memcache entry")
        for item in data:
            self.assertEqual(
                result_arr["data"][0][item],
                data[item],
                "Correct value for " + item)


    def test_save_multiple(self):
        """
        Save spread data with multiple entries to memcache
        """
        data = [
            DataBlobFactory().generate_data(type="spread"),
            DataBlobFactory().generate_data(type="spread")
        ]
        result_str = ""
        result_arr = []

        result = self.spread_memcache.save(self.week, data)
        self.assertEqual(
            result,
            len(data),
            "Saved the correct amount of data")

        result_str = memcache.get(
            self.spread_memcache._SpreadMemcache__tag(self.week))
        self.assertIsNotNone(
            result_str,
            "Memcache hit")

        result_arr = json.loads(result_str)
        for i in range(0, len(result_arr["data"])):
            for item in data[i]:
                self.assertEqual(
                    result_arr["data"][i][item],
                    data[i][item],
                    "Data " + item + " matches")


class TestSpreadAbstract(unittest.TestCase):
    def setUp(self):
        self.spread = Spread()
        self.week = 1

    def test_initial(self):
        self.assertIsNone(
            self.spread.next,
            "Testing initial state")

    def test_fetch_is_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.spread.fetch(self.week),

    def test_protected_fetch_is_unimplemented(self):
        with self.assertRaises(NotImplementedError):
            self.spread._fetch_spread(self.week)

    def test_save_is_not_implemented(self):
        data = {}

        with self.assertRaises(NotImplementedError):
            self.spread.save(self.week, data),


    def test_protected_save_is_unimplemented(self):
        data = {}

        with self.assertRaises(NotImplementedError):
            self.spread._save_spread(self.week, data)

class TestSpreadDatastore(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()

        self.datastore = SpreadDatastore()
        self.timestamp = int(datetime.datetime.now().strftime('%s'))
        self.week = self.timestamp % 1000 + 50
        self.factory = DataBlobFactory()
        self.game_id = unicode(self.timestamp % 1000 + 10000)

    def tearDown(self):
        self.testbed.deactivate()

    def test_super_class(self):
        self.assertTrue(
            issubclass(SpreadDatastore, Spread),
            "SpreadDatstore is a subclass of Spread")

    def test_missing_next_chain(self):
        self.assertIsNone(
            self.datastore.next,
            "Default doesn't have next in chain")

    def test_basic_fetch(self):
        result_arr = []
        result = {}
        test_data = self.factory.generate_data(week=self.week, type='spread')
        test_data[self.game_id] = ['San Francisco']

        self.assertTrue(
            SpreadModel(**test_data).put(),
            'Put data in the database')

        result_arr = self.datastore.fetch(self.week)
        self.assertIsNotNone(
            result_arr,
            "Datastore got us a result")
        self.assertEqual(
            len(result_arr),
            1,
            "Only 1 item in the datastore")

        result = result_arr[0]
        for key in test_data:
            self.assertTrue(key in result, 'Result has key "' + key + '"')
            self.assertEqual(
                test_data[key],
                result[key],
                'Value for key "' + key + '" matches')

    def test_basic_save(self):
        test_data = self.factory.generate_data(week=self.week, type='spread')
        test_data[self.game_id] = ['Green Bay']
        result = 0
        result_arr = []
        result_data = {}

        result = self.datastore.save(self.week, [test_data])
        self.assertEqual(
            1,
            result,
            'Saved exactly 1 entry')

        result_arr = SpreadModel().all().fetch(2)
        self.assertEqual(
            len(result_arr),
            1,
            "Fetch exactly 1 entry")

        result_data = result_arr[0]
        for key in test_data:
            self.assertTrue(hasattr(result_data, key), 'Result has key "' + key + '"' )
            self.assertEqual(
                test_data[key],
                getattr(result_data, key),
                'Value for key "' + key + '" matches')

    def test_basic_save_longer_entry(self):
        test_data = self.factory.generate_data(week=self.week, type='spread')
        test_data[self.game_id] = ['Houston', 'Under', 39]
        result = 0
        result_arr = []
        result_data = {}

        result = self.datastore.save(self.week, [test_data])
        self.assertEqual(
            1,
            result,
            'Saved exactly 1 entry')

        result_arr = SpreadModel().all().fetch(2)
        self.assertEqual(
            len(result_arr),
            1,
            'Fetch exactly 1 entry')

        result_data = result_arr[0]
        for key in test_data:
            self.assertTrue(hasattr(result_data, key), 'Result has key "' + key + '"')

            target = getattr(result_data, key)
            if isinstance(target, list):
                for item in target:
                    self.assertTrue(
                        item in test_data[key],
                        'Sub-item matches')
            else:
                self.assertEqual(
                    test_data[key],
                    getattr(result_data, key),
                    'Value for key "' + key + '" matches')

    def test_update_additions(self):
        initial_test_data = self.factory.generate_data(week=self.week, type='spread')
        initial_test_data[self.game_id] = ['Carolina']
        test_data = {}
        second_game_id = 0
        result = 0
        result_arr = []

        SpreadModel(**initial_test_data).put()
        test_data = self.factory.generate_data(week=self.week, type='spread')
        second_game_id = unicode(self.timestamp % 1000 + 10001)
        test_data[second_game_id] = ['Oakland']

        result = self.datastore.save(self.week, [test_data])
        self.assertEqual(
            1,
            result,
            'Saved exactly 1 entry')

        result_arr = SpreadModel().all().fetch(2)
        self.assertEqual(
            len(result_arr),
            1,
            'Fetch exactly 1 entry')

        result = result_arr[0]
        for key in initial_test_data:
            self.assertTrue(hasattr(result, key), 'Result has key "' + key + '"')
            self.assertEqual(
                initial_test_data[key],
                getattr(result, key),
                'Value for key "' + key + '" matches')

        for key in test_data:
            self.assertTrue(hasattr(result, key), 'Result has key "' + key + '"')
            self.assertEqual(
                test_data[key],
                getattr(result, key),
                'Value for key "' + key + '" matches')


    def test_update_replacement(self):
        pass

    def test_different_years(self):
        test_comparison = self.factory.generate_data(week=self.week, type='spread')
        test_data = [
            self.factory.generate_data(week=self.week, type='spread'),
            test_comparison
            ]
        old_owner = 'Protoman'
        result_arr = []
        result = {}

        test_data[0][sd.SPREAD_OWNER] = old_owner
        test_data[0]['year'] = 2013

        for item in test_data:
            SpreadModel(**item).put()

        result_arr = self.datastore.fetch(self.week)

        self.assertIsNotNone(
            result_arr,
            "Datastore got us a result")
        self.assertEqual(
            len(result_arr),
            1,
            "Only 1 item in the datastore")

        result = result_arr[0]
        for key in test_comparison:
            self.assertTrue(key in result, 'Result has key "' + key + '"')
            self.assertEqual(
                test_comparison[key],
                result[key],
                'Value for key "' + key + '" matches')


class TestSpreadFilter(unittest.TestCase):
    class TestMockSpread(Spread):
        def __init__(self, test_data):
            self.test_data = test_data
            super(TestSpreadFilter.TestMockSpread, self).__init__()

        def _fetch_spread(self, week):
            #self.test_data['unit_test'].assertEqual(self.test_data['expected_week'],week,'week matches')
            return self.test_data['expected_result']

        def _save_spread(self, week, data):
            #self.test_data['unit_test'].assertEqual(self.test_data['expected_week'],week,'week matches')
            return self.test_data['expected_result']

    def setUp(self):
        self.factory = DataBlobFactory()
        self.timestamp = int(datetime.datetime.now().strftime('%s'))
        self.week = self.timestamp % 40 + 50

        self.test_data = {
            "unit_test": self,
            "expected_week": self.week + nfl.WEEK_PREFIX['REG'],
            "expected_result": self.factory.generate_data(week=self.week, type='spread')
        }
        self.spread_filter = SpreadFilter(self.TestMockSpread(self.test_data))

    def test_init(self):
        spread_filter = SpreadFilter()

        # Test super class
        self.assertTrue(
            issubclass(SpreadFilter, Spread),
            "SpreadFilter is a subclass of Spread")
        # Validate there's nothing in the chain by default
        self.assertIsNone(
            spread_filter.next,
            "Default doesn't have next in chain")

    def test_fetch_basic(self):
        expected_result = self.test_data['expected_result']
        result = []

        result = self.spread_filter.fetch(self.week)
        for key in expected_result:
            self.assertTrue(key in result, 'Result has the correct key')

            self.assertEqual(expected_result[key],
                             result[key],
                             'Result values match')

            self.assertEqual(self.week,
                             result['week'],
                             'Week seems unmodified')


    def test_fetch_fail_if_not_chained(self):
        spread_filter = SpreadFilter()

        self.assertIsNone(spread_filter.fetch(self.week),
                          'Fetch (expectedly) returned nothing')


    def test_save_basic(self):
        expected_result = self.test_data['expected_result']
        result = []

        result = self.spread_filter.save(self.week, expected_result)
        for key in expected_result:
            self.assertTrue(key in result, 'Result has the correct key')

            self.assertEqual(expected_result[key],
                             result[key],
                             'Result values match')

            self.assertEqual(self.week,
                             result['week'],
                             'Week seems unmodified')


    def test_fetch_week_untouched_if_beyond_preseason_threshold(self):
        week = nfl.WEEK_PREFIX['PRE'] + self.week
        self.test_data['expected_week'] = week
        expected_result = self.test_data['expected_result']
        spread_filter = SpreadFilter(self.TestMockSpread(self.test_data))

        result = self.spread_filter.fetch(week)
        for key in expected_result:
            self.assertTrue(key in result, 'Result has the correct key')

            self.assertEqual(expected_result[key],
                             result[key],
                             'Result values match')


    def test_save_week_untouched_if_beyond_preseason_threshold(self):
        week = nfl.WEEK_PREFIX['PRE'] + self.week
        self.test_data['expected_week'] = week
        expected_result = self.test_data['expected_result']
        spread_filter = SpreadFilter(self.TestMockSpread(self.test_data))

        result = self.spread_filter.save(week, expected_result)
        for key in expected_result:
            self.assertTrue(key in result, 'Result has the correct key')

            self.assertEqual(expected_result[key],
                             result[key],
                             'Result values match')
