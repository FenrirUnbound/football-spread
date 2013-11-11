#! /usr/bin/env python
from __future__ import unicode_literals

import datetime
import json
import unittest

from test_lib.datablob_factory import DataBlobFactory

from lib.constants import DATA_BLOB as d
from lib.constants import HTTP_CODE as http_code
from lib.constants import NFL as nfl
from lib.constants import SCOREBOARD as sb

from models.score import Score
from models.score import ScoreModel
from models.score import _ScoreDatastore as ScoreDatastore
from models.score import _ScoreMemcache as ScoreMemcache
from models.score import _ScoreSource as ScoreSource
from models.score import _ScoreFilter as ScoreFilter

from google.appengine.api import memcache
from google.appengine.ext import testbed

from test_lib.mock_service import UrlFetchMock

class TestScoreModel(unittest.TestCase):
    def test_initialization(self):
        model = ScoreModel()
        test_points = {
            'year': 999,
            'week': 999,
            'away_name': "",
            'away_score': 0,
            'home_name': "",
            'home_score': 0,
            'game_clock': "00:00",
            'game_day': "Sun",
            'game_status': "",
            'game_tag': "",
            'game_time': "00:00",
            'game_id': 0,
            'spread_odds': 0.000,
            'spread_margin': 0.000,
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

        # Test fields with non-default values
        self.assertTrue(
            hasattr(model, 'timestamp'),
            "Has timestamp")

class TestScoreAbstract(unittest.TestCase):
    def setUp(self):
        self.score = Score()
        self.week = 1

    def tearDown(self):
        pass

    def test_initial(self):
        self.assertIsNone(
            self.score.next,
            "Testing initial state")

    def test_fetch_is_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.score.fetch(self.week),

    def test_protected_fetch_is_unimplemented(self):
        with self.assertRaises(NotImplementedError):
            self.score._fetch_score(self.week)

    def test_save_is_not_implemented(self):
        data = {}

        with self.assertRaises(NotImplementedError):
            self.score.save(self.week, data),


    def test_protected_save_is_unimplemented(self):
        data = {}

        with self.assertRaises(NotImplementedError):
            self.score._save_score(self.week, data)

class TestScoreMemcache(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_memcache_stub()

        self.score_memcache = ScoreMemcache()

        self.factory = DataBlobFactory()
        self.timestamp = int(datetime.datetime.now().strftime('%s'))
        self.week = self.timestamp % 1000 + 50

    def tearDown(self):
        self.testbed.deactivate()

    def test_super_class(self):
        self.assertTrue(
            issubclass(ScoreMemcache, Score),
            "ScoreMemcache is a subclass of Score")

    def test_missing_next_chain(self):
        self.assertIsNone(
            self.score_memcache.next,
            "Default doesn't have next in chain")

    def test_fetch_basic(self):
        data = self.factory.generate_data(
            timestamp=self.timestamp,
            week=self.week)
        tag = "SCORES_S2013W" + unicode(self.week)
        result = {}

        result = self.score_memcache.fetch(self.week)
        self.assertIsNone(
            result,
            "Memcache miss")

        memcache.add(tag, json.dumps(data))

        result = self.score_memcache.fetch(self.week)
        self.assertIsNotNone(
            result,
            "Memcache hit")
        self.assertEqual(
            result[d.GAME_WEEK],
            self.week,
            "Week is the same")
        self.assertEqual(
            result[d.NFL_GAME_ID],
            data['data'][d.NFL_GAME_ID],
            "NFL game ID matches")

    def test_save(self):
        data = [
            self.factory.generate_data(week=self.week)
        ]
        result = 0
        result_dict = {}
        result_str = ""
        tag = "SCORES_S2013W" + unicode(self.week)
        
        result = self.score_memcache.save(self.week, data)
        self.assertEqual(
            result,
            1,
            "Memcached exactly 1 item")

        result_str = memcache.get(tag)
        result_dict = json.loads(result_str)
        self.assertEqual(
            result_dict['data'][0][d.GAME_WEEK],
            self.week,
            "Week is the same")
        self.assertEqual(
            result_dict['data'][0][d.NFL_GAME_ID],
            data[0][d.NFL_GAME_ID],
            "NFL game ID matches")


    def test_tag_creation(self):
        tag = "SCORES_S2013W" + unicode(self.week)

        result_str = self.score_memcache._ScoreMemcache__tag(self.week)
        self.assertEqual(
            result_str,
            tag,
            "Tag creation")

    def test_save_multiple(self):
        data = [
            self.factory.generate_data(week=self.week),
            self.factory.generate_data(week=self.week+1),
            self.factory.generate_data(week=self.week+2)
        ]
        result = 0

        result = self.score_memcache.save(self.week, data)
        self.assertEqual(
            result,
            3,
            "Memcached exactly 3 item")

    @unittest.skip("Should not have to check for input type")
    def test_save_non_list(self):
        """
        Non-list data is passed in to save
        """
        data = self.factory.generate_data(week=self.week)
        result = 0
        result_dict = {}
        result_str = ""
        tag = "SCORES_S2013W" + unicode(self.week)
        
        result = self.score_memcache.save(self.week, data)
        self.assertEqual(
            result,
            1,
            "Memcached exactly 1 item")

        result_str = memcache.get(tag)
        result_dict = json.loads(result_str)
        self.assertEqual(
            result_dict['data'][d.GAME_WEEK],
            self.week,
            "Week is the same")
        self.assertEqual(
            result_dict['data'][d.NFL_GAME_ID],
            data[d.NFL_GAME_ID],
            "NFL game ID matches")

    def test_save_incremental(self):
        """
        Subsequent saves should add or replace information, not delete.
        """
        data = self.factory.generate_data(week=self.week)
        result = 0
        result_dict = {}
        result_str = ""
        tag = "SCORES_S2013W" + unicode(self.week)
        update_data = {}

        result = self.score_memcache.save(self.week, [data])
        self.assertEqual(
            result,
            1,
            "Memcached exactly 1 item")

        result_str = memcache.get(tag)
        result_dict = json.loads(result_str)
        self.assertEqual(
            result_dict['data'][0][d.GAME_WEEK],
            self.week,
            "Week is the same")
        self.assertEqual(
            result_dict['data'][0][d.NFL_GAME_ID],
            data[d.NFL_GAME_ID],
            "NFL game ID matches")
        result_dict = json.loads(result_str)
        self.assertEqual(
            result_dict['data'][0][d.HOME_SCORE],
            data[d.HOME_SCORE],
            "Home score is the same")
        self.assertEqual(
            result_dict['data'][0][d.HOME_NAME],
            data[d.HOME_NAME],
            "Home name is the same")

        update_data = {
            d.GAME_WEEK: self.week,
            d.NFL_GAME_ID: data[d.NFL_GAME_ID],
            d.HOME_SCORE: data[d.HOME_SCORE] + 7
        }

        result = self.score_memcache.save(self.week, [update_data])
        self.assertEqual(
            result,
            1,
            "Memcached exactly 1 item")

        result_str = memcache.get(tag)
        result_dict = json.loads(result_str)
        self.assertEqual(
            result_dict['data'][0][d.GAME_WEEK],
            self.week,
            "Week is the same")
        self.assertEqual(
            result_dict['data'][0][d.NFL_GAME_ID],
            update_data[d.NFL_GAME_ID],
            "NFL game ID matches")
        result_dict = json.loads(result_str)
        self.assertEqual(
            result_dict['data'][0][d.HOME_SCORE],
            update_data[d.HOME_SCORE],
            "Home score is the same")
        self.assertIsNotNone(
            result_dict['data'][0][d.HOME_NAME],
            "Home name exists in result")
        self.assertEqual(
            result_dict['data'][0][d.HOME_NAME],
            data[d.HOME_NAME],
            "Home name is the same")

    def test_validate_data(self):
        """
        Verify helper function validates data
        """
        data = self.factory.generate_data(week=self.week)
        multiple_data = []
        result = None

        result = self.score_memcache._ScoreMemcache__validate_data([data])
        for key in data:
            self.assertEqual(
                data[key],
                result[0][key],
                key + " matches")

        data['GreateNess'] = 'awaits'
        result = self.score_memcache._ScoreMemcache__validate_data([data])
        self.assertFalse(
            "GreateNess" in result[0],
            "Extraneous data omitted")

        mult_data = [
            data,
            self.factory.generate_data(week=self.week)
        ]
        result = self.score_memcache._ScoreMemcache__validate_data(mult_data)
        for index, game in enumerate(result):
            for key in game:
                self.assertEqual(
                    mult_data[index][key],
                    game[key],
                    key + " matches")

    def test_sync_with_scores_no_data(self):
        """
        Validate the helper function updates when there isn't
        any data in Memcache
        """
        data = [
            self.factory.generate_data(week=self.week)
        ]
        result = None

        result = self.score_memcache._ScoreMemcache__sync_with_scores(
            self.week,
            data)

        self.assertIsNotNone(
            result,
            "sync_with_scores returned a value")
        self.assertEqual(
            len(result),
            len(data),
            "Result contains the correct amount of elements")

        for index, game in enumerate(data):
            for key in data[index]:
                self.assertEqual(
                    data[index][key],
                    result[index][key],
                    key + " matches")


    def test_sync_with_scores(self):
        """
        Validate the helper function updates
        """
        data = [
            self.factory.generate_data(week=self.week),
            self.factory.generate_data(week=self.week),
            self.factory.generate_data(week=self.week)
        ]
        to_update = 1
        update_data = data[to_update]
        result = None
        result_int = 0

        # Prepopulate memcache
        result_int = self.score_memcache.save(self.week, data)
        self.assertEqual(
            len(data),
            result_int,
            "Correct number of elements saved")

        update_data[d.HOME_SCORE] += 14
        result = self.score_memcache._ScoreMemcache__sync_with_scores( 
            self.week, 
            [update_data])

        self.assertIsNotNone(
            result,
            "sync_with_scores returned a value")
        self.assertEqual(
            len(result),
            len(data),
            "Result contains the correct amount of elements")


        for index, game in enumerate(data):
            if index != to_update:
                for key in data[index]:
                    self.assertEqual(
                        data[index][key],
                        result[index][key],
                        key + " matches for index " + unicode(index))
            else:
                for key in update_data:
                    self.assertEqual(
                        update_data[key],
                        result[index][key],
                        key + " matches for index " + unicode(index))

    def test_save_additional_field(self):
        """
        Validate memcache updates when a field previously not recorded
        (i.e., spread-related data) is given to be added.
        """
        data = self.factory.generate_data(week=self.week)
        result = 0
        result_dict = {}
        result_str = ""
        spread_margin = data[d.SPREAD_MARGIN]
        spread_odds = data[d.SPREAD_ODDS]
        tag = "SCORES_S2013W" + unicode(self.week)
        update_data = {}

        # Remove fields to be added during this test
        del data[d.SPREAD_MARGIN]
        del data[d.SPREAD_ODDS]

        result = self.score_memcache.save(self.week, [data])
        self.assertEqual(
            result,
            1,
            "Memcached exactly 1 item")

        # Validate preloaded data in memcache
        result_str = memcache.get(tag)
        result_dict = json.loads(result_str)
        self.assertEqual(
            result_dict['data'][0][d.GAME_WEEK],
            self.week,
            "Week is the same")
        self.assertEqual(
            result_dict['data'][0][d.NFL_GAME_ID],
            data[d.NFL_GAME_ID],
            "NFL game ID matches")
        result_dict = json.loads(result_str)
        self.assertEqual(
            result_dict['data'][0][d.HOME_SCORE],
            data[d.HOME_SCORE],
            "Home score is the same")
        self.assertEqual(
            result_dict['data'][0][d.HOME_NAME],
            data[d.HOME_NAME],
            "Home name is the same")

        update_data = {
            d.GAME_WEEK: self.week,
            d.NFL_GAME_ID: data[d.NFL_GAME_ID],
            d.HOME_SCORE: data[d.HOME_SCORE],
            d.SPREAD_ODDS: spread_odds,
            d.SPREAD_MARGIN: spread_margin
        }

        result = self.score_memcache.save(self.week, [update_data])
        self.assertEqual(
            result,
            1,
            "Memcached exactly 1 item")

        result_str = memcache.get(tag)
        result_dict = json.loads(result_str)
        self.assertEqual(
            result_dict['data'][0][d.GAME_WEEK],
            self.week,
            "Week is the same")
        self.assertEqual(
            result_dict['data'][0][d.NFL_GAME_ID],
            update_data[d.NFL_GAME_ID],
            "NFL game ID matches")
        result_dict = json.loads(result_str)
        self.assertEqual(
            result_dict['data'][0][d.HOME_SCORE],
            update_data[d.HOME_SCORE],
            "Home score is the same")
        self.assertIsNotNone(
            result_dict['data'][0][d.HOME_NAME],
            "Home name exists in result")
        self.assertEqual(
            result_dict['data'][0][d.HOME_NAME],
            data[d.HOME_NAME],
            "Home name is the same")
        self.assertEqual(
            result_dict['data'][0][d.SPREAD_MARGIN],
            spread_margin,
            "Spread margin is the same")
        self.assertEqual(
            result_dict['data'][0][d.SPREAD_ODDS],
            spread_odds,
            "Spread odds are the same")


class TestScoreDatastore(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()

        self.score_datastore = ScoreDatastore()

        self.factory = DataBlobFactory()
        self.timestamp = int(datetime.datetime.now().strftime('%s'))
        self.week = self.timestamp % 1000 + 50

    def tearDown(self):
        self.testbed.deactivate()

    def test_init(self):
        # Test super class
        self.assertTrue(
            issubclass(ScoreDatastore, Score),
            "ScoreMemcache is a subclass of Score")
        # Validate there's nothing in the chain by default
        self.assertIsNone(
            self.score_datastore.next,
            "Default doesn't have next in chain")

    def test_fetch_basic(self):
        """
        Test basic fetch operation
        """
        data = self.factory.generate_data(week=self.week)
        result = 0

        self.assertTrue(
            ScoreModel(**data).put(),
            "Put data into database")

        result = self.score_datastore.fetch(self.week)
        self.assertIsNotNone(
            result,
            "Datastore got us a result")
        self.assertEqual(
            len(result),
            1,
            "Only 1 game in the datastore")
        self.assertEqual(
            result[0][d.HOME_SCORE],
            data[d.HOME_SCORE],
            "Home score is the same")
        self.assertEqual(
            result[0][d.AWAY_SCORE],
            data[d.AWAY_SCORE],
            "Aways score is the same")
        self.assertEqual(
            result[0][d.NFL_GAME_ID],
            data[d.NFL_GAME_ID],
            "NFL game ID matches")
        self.assertEqual(
            result[0][d.GAME_WEEK],
            data[d.GAME_WEEK],
            "Season week matches")

    def test_save_basic(self):
        """
        Test basic save operation
        """
        data = self.factory.generate_data(week=self.week)
        result = 0
        result_arr = []

        result = self.score_datastore.save(self.week, [data])
        self.assertEqual(
            result,
            1,
            "Saved exactly 1 entry")

        result_arr = ScoreModel().all().fetch(2)
        self.assertEqual(
            len(result_arr),
            1,
            "Fetch exactly 1 entry")
        self.assertEqual(
            result_arr[0].away_score,
            data[d.AWAY_SCORE],
            "Away score is the same")
        self.assertEqual(
            result_arr[0].home_score,
            data[d.HOME_SCORE],
            "Home score is the same")
        self.assertEqual(
            result_arr[0].game_id,
            data[d.NFL_GAME_ID],
            "NFL game ID matches")
        self.assertEqual(
            result_arr[0].week,
            data[d.GAME_WEEK],
            "Season week matches")
        self.assertIsNotNone(
            result_arr[0].timestamp,
            "Timestamp is present")

    def test_save_updates(self):
        """
        Saving when a pre-existing entry is present leads to the data
        being updated instead.
        """
        data = self.factory.generate_data(week=self.week)
        increment_score = 120
        result = 0
        result_arr = []
        timestamp = None

        # Preload data into the datastore
        self.assertTrue(
            ScoreModel(**data).put(),
            "Preload successful")

        timestamp = ScoreModel().all().fetch(1)[0].timestamp

        data[d.HOME_SCORE] += increment_score
        result = self.score_datastore.save(self.week, [data])
        self.assertEqual(
            result,
            1,
            "Saved exactly 1 entry")

        result_arr = ScoreModel().all().fetch(2)
        self.assertEqual(
            len(result_arr),
            1,
            "Fetch exactly 1 entry")
        self.assertEqual(
            result_arr[0].home_score,
            data[d.HOME_SCORE],
            "Data was updated")
        self.assertTrue(
            timestamp < result_arr[0].timestamp,
            "Timestamp was updated")

    def test_save_multiple_updates(self):
        """
        Multiple saves, when pre-existing entries are present, lead
        to data being updated instead
        """
        data = [
            self.factory.generate_data(week=self.week),
            self.factory.generate_data(week=self.week),
            self.factory.generate_data(week=self.week)
        ]
        increment_score = 120
        result = 0
        result_arr = []

        # Preload data
        ScoreModel(**data[0]).put()
        ScoreModel(**data[1]).put()
        ScoreModel(**data[2]).put()

        # Modify data
        data[0][d.HOME_SCORE] += increment_score
        data[1][d.AWAY_SCORE] += increment_score
        result = self.score_datastore.save(self.week, data)
        self.assertEqual(
            result,
            3,
            "Saved exactly 3 entries [" + unicode(result) + "]")

        result_arr = ScoreModel().all().fetch(4)
        self.assertEqual(
            len(result_arr),
            3,
            "Fetch exactly 3 entries")
        self.assertEqual(
            result_arr[0].home_score,
            data[0][d.HOME_SCORE],
            "Data was updated")
        self.assertEqual(
            result_arr[1].away_score,
            data[1][d.AWAY_SCORE],
            "Data was updated")
        self.assertEqual(
            result_arr[2].home_score,
            data[2][d.HOME_SCORE],
            "Data is untouched")

    def test_saves_and_updates(self):
        """
        Saving with a mix of data that's pre-existing and new
        """
        data = [
            self.factory.generate_data(week=self.week),
            self.factory.generate_data(week=self.week),
            self.factory.generate_data(week=self.week)
        ]
        increment_score = 120
        result = 0
        result_arr = []
        timestamp_dynamic = None
        timestamp_static = None

        # Order the data by increasing nfl_game_id
        data[1][d.NFL_GAME_ID] += 10000
        data[2][d.NFL_GAME_ID] += 30000

        # Preload data
        ScoreModel(**data[0]).put()
        ScoreModel(**data[2]).put()

        result_arr = ScoreModel().all().order("game_id").fetch(2)
        timestamp_dynamic = result_arr[0].timestamp     # 0'th data entry
        timestamp_static = result_arr[1].timestamp      # 2nd data entry

        # Modify data
        data[0][d.HOME_SCORE] += increment_score
        data[1][d.AWAY_SCORE] += increment_score
        result = self.score_datastore.save(123456, data)
        self.assertEqual(
            result,
            3,
            "Saved exactly 3 entries")

        result_arr = ScoreModel().all().order("game_id").fetch(4)
        self.assertEqual(
            len(result_arr),
            3,
            "Fetch exactly 3 entries")
        self.assertEqual(
            result_arr[0].home_score,
            data[0][d.HOME_SCORE],
            "Home score was updated")
        self.assertTrue(
            timestamp_dynamic < result_arr[0].timestamp,
            "Game 0 timestamp was updated")
        self.assertEqual(
            result_arr[1].away_score,
            data[1][d.AWAY_SCORE],
            "Game 1 is ok")
        self.assertEqual(
            result_arr[2].home_score,
            data[2][d.HOME_SCORE],
            "Data is untouched")
        self.assertTrue(
            timestamp_static < result_arr[2].timestamp,
            "Game 2 timestamp is unchanged")

    def test_stale_data_threshold(self):
        """
        Test against the threshold property for considering data as stale
        """
        self.assertEqual(
            getattr(ScoreDatastore, "_ScoreDatastore__THRESHOLD"),
            300,
            "Threshold is at 300")

    @unittest.skip("Timestamp is always unmodifiable via auto_now option")
    def test_stale_data_fetch(self):
        """
        Verify that the datstore rejects data that is considered stale.
        """
        data = self.factory.generate_data(week=self.week)
        threshold = datetime.timedelta(
            seconds=getattr(ScoreDatastore, '_ScoreDatastore__THRESHOLD'))
        data[d.TIMESTAMP] = datetime.datetime.utcnow() - threshold
        result_arr = []

        ScoreModel(**data).put()
        result_arr = ScoreModel().all().fetch(2)
        self.assertEqual(
            len(result_arr),
            1,
            "One entry pre-loaded in the datastore")

        result_arr = self.score_datastore.fetch(self.week)
        self.assertEqual(
            len(result_arr),
            0,
            "Datastore returned an empty list")



class TestScoreSource(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_urlfetch_stub()
        # Create the mocked service & inject it into the testbed
        self.fetch_mock = UrlFetchMock()
        self.testbed._register_stub(testbed.URLFETCH_SERVICE_NAME, self.fetch_mock)

        self.score_source = ScoreSource()
        self.factory = DataBlobFactory()
        self.timestamp = int(datetime.datetime.now().strftime('%s'))
        self.week = self.timestamp % 1000 + 50
        self.content_str = (
            "{\"ss\":[[\"Sun\",\"8:00\",\"Pregame\",,\"SF\",,"
            "\"BAL\",,,,\"56093\",,\"PRE0\",\"2013\"]]}").encode("UTF-8")

    def tearDown(self):
        self.testbed.deactivate()

    def test_init(self):
        # Test super class
        self.assertTrue(
            issubclass(ScoreSource, Score),
            "ScoreMemcache is a subclass of Score")
        # Validate there's nothing in the chain by default
        self.assertIsNone(
            self.score_source.next,
            "Default doesn't have next in chain")

    def test_fetch(self):
        data = {
            "content": self.content_str,
            "final_url": (sb.URL_REG).encode("UTF-8"),
            "status_code": 200
        }
        self.fetch_mock.set_return_values(**data)

        result = self.score_source.fetch(self.week)
        self.assertIsNotNone(
            result,
            "Source fetch was successful")

    def test_fetch_not_ok(self):
        data = {
            "content": self.content_str,
            "final_url": (sb.URL_REG).encode("UTF-8"),
            "status_code": 201
        }
        self.fetch_mock.set_return_values(**data)

        result = self.score_source.fetch(self.week)
        self.assertIsNone(
            result,
            "Source fetch was (purposefully) unsuccessful.")

    def test_save(self):
        """
        Verify save returns the number of elements requested to be
        saved.
        """
        data = [
            self.factory.generate_data(1234),
            self.factory.generate_data(1235),
            self.factory.generate_data(1236),
        ]
        result = 0

        result = self.score_source.save(self.week, data)
        self.assertEqual(
            result,
            len(data),
            "Received correct quantity")

class TestScoreFilter(unittest.TestCase):
    class TestMockScore(Score):
        def __init__(self, test_data):
            self.test_data = test_data
            super(TestScoreFilter.TestMockScore, self).__init__()  

        def _fetch_score(self, week):
            self.test_data['unit_test'].assertEqual(
                self.test_data['expected_week'],
                week,
                'week matches')
            return self.test_data['expected_result']

        def _save_score(self, week, data):
            self.test_data['unit_test'].assertEqual(
                self.test_data['expected_week'],
                week,
                'week matches')
            return self.test_data['expected_result']

    def setUp(self):
        self.factory = DataBlobFactory()
        self.timestamp = int(datetime.datetime.now().strftime('%s'))
        self.week = self.timestamp % 40 + 50

        self.test_data = {
            "unit_test": self,
            "expected_week": self.week + nfl.WEEK_PREFIX['REG'],
            "expected_result": self.factory.generate_data(week=self.week)
        }
        self.score_filter = ScoreFilter(self.TestMockScore(self.test_data))

    def test_init(self):
        score_filter = ScoreFilter()

        # Test super class
        self.assertTrue(
            issubclass(ScoreFilter, Score),
            "ScoreMemcache is a subclass of Score")
        # Validate there's nothing in the chain by default
        self.assertIsNone(
            score_filter.next,
            "Default doesn't have next in chain")

    def test_fetch_basic(self):
        expected_result = self.test_data['expected_result']
        result = []

        result = self.score_filter.fetch(self.week)
        for key in expected_result:
            self.assertTrue(key in result, 'Result has the correct key')

            self.assertEqual(expected_result[key],
                             result[key],
                             'Result values match')

            self.assertEqual(self.week,
                             result['week'],
                             'Week seems unmodified')

    def test_fetch_fail_if_not_chained(self):
        score_filter = ScoreFilter()

        self.assertIsNone(score_filter.fetch(self.week),
                          'Fetch (expectedly) returned nothing')

    def test_save_basic(self):
        expected_result = self.test_data['expected_result']
        result = []

        result = self.score_filter.save(self.week, expected_result)
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
        score_filter = ScoreFilter(self.TestMockScore(self.test_data))

        result = self.score_filter.fetch(week)
        for key in expected_result:
            self.assertTrue(key in result, 'Result has the correct key')

            self.assertEqual(expected_result[key],
                             result[key],
                             'Result values match')

    def test_save_week_untouched_if_beyond_preseason_threshold(self):
        week = nfl.WEEK_PREFIX['PRE'] + self.week
        self.test_data['expected_week'] = week
        expected_result = self.test_data['expected_result']
        score_filter = ScoreFilter(self.TestMockScore(self.test_data))

        result = self.score_filter.save(week, expected_result)
        for key in expected_result:
            self.assertTrue(key in result, 'Result has the correct key')

            self.assertEqual(expected_result[key],
                             result[key],
                             'Result values match')
