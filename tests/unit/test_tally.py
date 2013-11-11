from __future__ import unicode_literals

import datetime
import unittest

from google.appengine.api import memcache
from google.appengine.ext import testbed


from models.tally import TallyModel
from models.tally import _TallyDatastore as TallyDatastore
from models.tally import TallyCalculator

from models.spread import SpreadFactory
from models.score import ScoreFactory
from models.score import ScoreModel

from test_lib.mock_service import UrlFetchMock

class TestTallyModel(unittest.TestCase):
    def test_initialization(self):
        model = TallyModel()
        test_points = {
            'year': 999,
            'week': 999,
            'owner': 'Nobody',
            'score': 0
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

class TestTallyDatastore(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()


        self.datastore = TallyDatastore()
        self.timestamp = int(datetime.datetime.now().strftime('%s'))
        self.week = self.timestamp % 1000 + 50

    def tearDown(self):
        self.testbed.deactivate()

    def test_basic_fetch(self):
        data = {
            'year': 2013,
            'week': self.week,
            'owner': 'MegaMan',
            'score': 12
        }
        result = []
        tally_data = {}

        self.assertTrue(
            TallyModel(**data).put(),
            "Put data into database")

        result = self.datastore.fetch(self.week)
        self.assertIsNotNone(
            result,
            "Datastore got us a result")

        tally_data = result[0]
        for key in data:
            self.assertTrue(key in tally_data, 
                            'Tally data has key "' + key + '"')

            self.assertEqual(data[key],
                             tally_data[key],
                             'Data for key "' + key + '" matches')

    def test_multiple_fetch(self):
        data = [
            {
                'year': 2013,
                'week': self.week,
                'owner': 'MegaMan',
                'score': 12
            },
            {
                'year': 2013,
                'week': self.week,
                'owner': 'Zero',
                'score': 8
            }
        ]
        result = []
        tally_data = {}


        for data_point in data:
            TallyModel(**data_point).put()

        result = self.datastore.fetch(self.week)
        self.assertIsNotNone(
            result,
            "Datastore got us a result")
        self.assertEqual(
            len(data),
            len(result),
            'Datastore returned the correct amount')

        for index, tally_data in enumerate(sorted(result, key=lambda k: k['owner'], reverse=False)):
            data_point = data[index]
            for key in data_point:
                self.assertTrue(key in tally_data, 
                                'Tally data has key "' + key + '"')

                self.assertEqual(data_point[key],
                                 tally_data[key],
                                 'Data for key "' + key + '" matches')

    def test_basic_save(self):
        data = [
            {
                'year': 2013,
                'week': self.week,
                'owner': 'MegaMan',
                'score': 12
            }
        ]

        self.assertEqual(
            len(data),
            self.datastore.save(self.week, data),
            'Datastore saved the correct amount')

        result = TallyModel.all().fetch(2)
        self.assertEqual(
            len(data),
            len(result),
            'Datastore has the correct amount')
        for data_point in data:
            for key in data_point:
                self.assertTrue(hasattr(result[0], key), 
                                'Has key "' + key + '"')
                self.assertEqual(data_point[key], 
                                 getattr(result[0], key), 
                                 'Value for key "' + key + '" matches')

    def test_multiple_save(self):
        data = [
            {
                'year': 2013,
                'week': self.week,
                'owner': 'MegaMan',
                'score': 12
            },
            {
                'year': 2013,
                'week': self.week,
                'owner': 'Zero',
                'score': 8
            }
        ]

        self.assertEqual(
            len(data),
            self.datastore.save(self.week, data),
            'Datastore saved the correct amount')

        result = TallyModel.all().order("owner").fetch(2)
        self.assertEqual(
            len(data),
            len(result),
            'Datastore has the correct amount')
        for index, data_point in enumerate(sorted(data, key=lambda k: k['owner'], reverse=False)):
            for key in data_point:
                self.assertTrue(hasattr(result[index], key), 
                                'Has key "' + key + '"')
                self.assertEqual(data_point[key], 
                                 getattr(result[index], key), 
                                 'Value for key "' + key + '" matches')

    def test_update_save(self):
        data = [
            {
                'year': 2013,
                'week': self.week,
                'owner': 'MegaMan',
                'score': 10
            }
        ]
        offset = 27

        TallyModel(**data[0]).put()

        data[0]['score'] += offset

        self.assertEqual(
            len(data),
            self.datastore.save(self.week, data),
            'Datastore saved the correct amount')

        result = TallyModel.all().fetch(2)
        self.assertEqual(
            len(data),
            len(result),
            'Datastore has the correct amount')
        for data_point in data:
            for key in data_point:
                self.assertTrue(hasattr(result[0], key), 
                                'Has key "' + key + '"')
                self.assertEqual(data_point[key], 
                                 getattr(result[0], key), 
                                 'Value for key "' + key + '" matches')

class TestTallyCalculator(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_urlfetch_stub()

        # Create the mocked service & inject it into the testbed
        self.fetch_mock = UrlFetchMock()
        self.testbed._register_stub(testbed.URLFETCH_SERVICE_NAME, self.fetch_mock)

        self.timestamp = int(datetime.datetime.now().strftime('%s'))
        self.week = self.timestamp % 1000 + 100

    def tearDown(self):
        self.testbed.deactivate()

    def test_basic_calculation(self):
        spread_data = [
            {
                'year': 2013,
                'week': self.week,
                'owner': 'MegaMan',
                '1234': ['HOU', 'UN', '49']
            },
            {
                'year': 2013,
                'week': self.week,
                'owner': 'Zero',
                '1234': ['HOU', 'OV', '59']
            },
            {
                'year': 2013,
                'week': self.week,
                'owner': 'Bass',
                '1234': ['SD', 'OV', '58']
            }
        ]
        score_data = [
            {
                'year': 2013,
                'week': self.week,
                'away_name': 'HOU',
                'away_score': 28,
                'home_name': 'SD',
                'home_score': 31,
                'game_id': 1234,
                'spread_odds': -3.5,
                'spread_margin': 49.5,
            }
        ]
        answer_key = {
            'MegaMan': 1,
            'Zero': 4,
            'Bass': 2
        }

        score = ScoreFactory().get_instance(depth=4)
        result = score.save(self.week, score_data)
        spread = SpreadFactory().get_instance()
        result = spread.save(self.week, spread_data)

        tallyator = TallyCalculator()

        result = tallyator.count(self.week)
        self.assertEqual(len(spread_data), 
                         len(result),
                         'Counted the right amount')
        for tally_data in result:
            expected_result = answer_key[tally_data['owner']]
            self.assertEqual(
                expected_result,
                tally_data['score'],
                'Expected result received (' + unicode(expected_result) + ')')

        result = TallyModel.all().fetch(4)
        self.assertEqual(len(spread_data), 
                         len(result),
                         'Datastore has the correct amount')

        for tally_data in result:
            expected_result = answer_key[tally_data.owner]
            self.assertEqual(
                expected_result,
                tally_data.score,
                'Expected result received (' + unicode(expected_result) + ')')


