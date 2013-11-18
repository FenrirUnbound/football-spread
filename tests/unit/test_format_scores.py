#! /usr/bin/env python
from __future__ import unicode_literals

import unittest

from lib.constants import DATA_BLOB as d
from lib.constants import NFL as nfl
from simplejson import JSONDecodeError

from models.format_scores import FormatFactory
from models.format_scores import Formatter
from test_lib.gamefeed_factory import GameFeedFactory

from models.format_scores import _FormatMapper as FormatMapper
from models.format_scores import _FormatOvertime as FormatOvertime
from models.format_scores import _FormatPadding as FormatPadding
from models.format_scores import _FormatUnicode as FormatUnicode

class TestFormatFactory(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_instance(self):
        product = FormatFactory().get_instance()
        self.assertIsNotNone(
            product,
            "Got instance from format factory")
        self.assertTrue(
            issubclass(product.__class__, Formatter),
            "Received a Formatter from format factory")

class TestFormatterAbstract(unittest.TestCase):
    def setUp(self):
        self.formatter = Formatter()
        self.input_str = "qwerasdfzxcv"

    def tearDown(self):
        pass

    def test_initial(self):
        self.assertIsNone(
            self.formatter.next,
            "Testing initial state")

    def test_format_is_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.formatter.format(self.input_str)

    def test_protected_format_is_unimplemented(self):
        with self.assertRaises(NotImplementedError):
            self.formatter._format(self.input_str)

class TestFormatPadding(unittest.TestCase):
    def setUp(self):
        self.formatter = FormatPadding(None)
        pass

    def tearDown(self):
        pass

    def test_creation(self):
        formatter = FormatPadding(None)

    def test_initial(self):
        # Check super class
        self.assertTrue(
            issubclass(FormatPadding, Formatter),
            "FormatPadding is a subclass of Formatter")

        # Check next chain is missing
        self.assertTrue(hasattr(self.formatter, "next"))
        self.assertIsNone(
            self.formatter.next,
            "Default doesn't have next in chain")

    def test_format_basic(self):
        input_str = "a,b,c,d,e,f,g"

        result = self.formatter.format(input_str)
        self.assertEquals(
            input_str,
            result,
            "Format did nothing")

    def test_format_nothing(self):
        input_str = ""

        result = self.formatter.format(input_str)
        self.assertEquals(
            input_str,
            result,
            "Input & result strings are equals")

    def test_format_to_pad(self):
        input_str = "a,b,c,,,,d,e,f"

        result = self.formatter.format(input_str)
        self.assertEquals(
            result,
            "a,b,c,0,0,0,d,e,f",
            "String was formatted properly")


class TestFormatOvertime(unittest.TestCase):
    def setUp(self):
        self.formatter = FormatOvertime(None)
        self.input_str = ""

    def tearDown(self):
        pass

    def test_initial(self):
        # Check super class
        self.assertTrue(
            issubclass(FormatPadding, Formatter),
            "FormatPadding is a subclass of Formatter")

        # Check next chain is missing
        self.assertTrue(hasattr(self.formatter, "next"))
        self.assertIsNone(
            self.formatter.next,
            "Default doesn't have next in chain")

    def test_format_nothing(self):
        self.input_str = ""

        result = self.formatter.format(self.input_str)
        self.assertEquals(
            self.input_str,
            result,
            "Input & result strings are equal")

    def test_format_basic(self):
        self.input_str = "a,b,Final Overtime,final,overtime,Final Overtime,g"

        result = self.formatter.format(self.input_str)
        self.assertEquals(
            self.input_str,
            result,
            "Format did nothing")

    def test_format_game_data_with_overtime(self):
        self.input_str = "a,b,c,final overtime,e,f,g"

        result = self.formatter.format(self.input_str)
        self.assertEquals(
            "a,b,c,Final Overtime,e,f,g",
            result,
            "String was formatted properly")

class TestFormatUnicode(unittest.TestCase):
    def setUp(self):
        self.formatter = FormatUnicode()

    def tearDown(self):
        pass

    def test_initial(self):
        # Check super class
        self.assertTrue(
            issubclass(FormatUnicode, Formatter),
            "FormatPadding is a subclass of Formatter")

        # Check next chain is missing
        self.assertTrue(hasattr(self.formatter, "next"))
        self.assertIsNone(
            self.formatter.next,
            "Default doesn't have next in chain")   

    def test_format_nothing(self):
        self.input_str = ""

        result = self.formatter.format(self.input_str)
        self.assertEquals(
            self.input_str,
            result,
            "Input & result strings are equal")

    def test_format_basic(self):
        self.input_str = "a,b,c,d,e,f,g"

        result = self.formatter.format(self.input_str)
        self.assertTrue(
            isinstance(result, unicode),
            "String is unicode string")

    def test_format_unicode_string(self):
        self.input_str = "a,b,c,d,e,f,g"

        result = self.formatter.format(self.input_str)
        self.assertTrue(
            isinstance(result, unicode),
            "String is unicode string")

class TestFormatMapper(unittest.TestCase):
    def setUp(self):
        self.formatter = FormatMapper()
        self.data_generator = GameFeedFactory()
    
    def tearDown(self):
        pass

    def test_initial(self):
        # Check super class
        self.assertTrue(
            issubclass(FormatUnicode, Formatter),
            "FormatPadding is a subclass of Formatter")

        # Check next chain is missing
        self.assertTrue(hasattr(self.formatter, "next"))
        self.assertIsNone(
            self.formatter.next,
            "Default doesn't have next in chain")

    def test_format_nothing(self):
        self.input_str = ""

        result = self.formatter.format(self.input_str)
        self.assertEquals(
            self.input_str,
            result,
            "Input & result strings are equal")

    def test_format_regular_season(self):
        self.input_str = self.data_generator.generate_data(data_type='REG')

        self.input_answer = [
            {
                d.AWAY_NAME: "MIN",
                d.AWAY_SCORE: 16,
                d.GAME_CLOCK: "",
                d.GAME_DAY: "Fri",
                d.GAME_SEASON: 2013,
                d.GAME_STATUS: "Final",
                d.GAME_TAG: "REG11",
                d.GAME_TIME: '7:00',
                d.GAME_WEEK: 11 + nfl.WEEK_PREFIX['REG'],
                d.HOME_NAME: 'BUF',
                d.HOME_SCORE: 20,
                d.NFL_GAME_ID: 56115
            },
            {
                d.AWAY_NAME: "SF",
                d.AWAY_SCORE: 15,
                d.GAME_CLOCK: "",
                d.GAME_DAY: "Fri",
                d.GAME_SEASON: 2013,
                d.GAME_STATUS: "Final",
                d.GAME_TAG: "REG11",
                d.GAME_TIME: "8:00",
                d.GAME_WEEK: 11 + nfl.WEEK_PREFIX['REG'],
                d.HOME_NAME: "KC",
                d.HOME_SCORE: 13,
                d.NFL_GAME_ID: 56116
            }
        ]

        result = self.formatter.format(self.input_str)
        self.assertIsNotNone(
            result,
            "Formatter succeeded")
        self.assertListEqual(
            result,
            self.input_answer,
            'Formatter returned the correct list')
        for (index, item) in enumerate(result):
            self.assertDictEqual(
                item,
                self.input_answer[index],
                'Formatter created the correct dict (' + unicode(index) + ')'
                )

    def test_format_post_season(self):
        self.input_str = self.data_generator.generate_data(data_type='POS')
        self.input_answer = [
            {
                d.AWAY_NAME: "BAL",
                d.AWAY_SCORE: 38,
                d.GAME_CLOCK: "",
                d.GAME_DAY: "Sat",
                d.GAME_SEASON: 2012,
                d.GAME_STATUS: "final overtime",
                d.GAME_TAG: "POST22",
                d.GAME_TIME: "4:30",
                d.GAME_WEEK: 22 + nfl.WEEK_PREFIX['POS'],
                d.HOME_NAME: "DEN",
                d.HOME_SCORE: 35,
                d.NFL_GAME_ID: 55829
            }
        ]

        result = self.formatter.format(self.input_str)
        self.assertIsNotNone(
            result,
            "Formatter succeeded")
        self.assertDictEqual(
            result[0],
            self.input_answer[0],
            "Formatter created the correct dict")

    def test_format_pre_season(self):
        self.input_str = self.data_generator.generate_data(data_type='PRE')

        self.input_answer = [
            {
                d.AWAY_NAME: "OAK",
                d.AWAY_SCORE: 20,
                d.GAME_CLOCK: "",
                d.GAME_DAY: "Fri",
                d.GAME_SEASON: 2013,
                d.GAME_STATUS: "Final",
                d.GAME_TAG: "PRE2",
                d.GAME_TIME: "8:00",
                d.GAME_WEEK: 2 + nfl.WEEK_PREFIX['PRE'],
                d.HOME_NAME: "NO",
                d.HOME_SCORE: 28,
                d.NFL_GAME_ID: 56117
            },
            {
                d.AWAY_NAME: "DAL",
                d.AWAY_SCORE: 0,
                d.GAME_CLOCK: "",
                d.GAME_DAY: "Sat",
                d.GAME_SEASON: 2013,
                d.GAME_STATUS: "Pregame",
                d.GAME_TAG: "PRE2",
                d.GAME_TIME: "4:30",
                d.GAME_WEEK: 2 + nfl.WEEK_PREFIX['PRE'],
                d.HOME_NAME: "ARI",
                d.HOME_SCORE: 0,
                d.NFL_GAME_ID: 56118
            }
        ]

        result = self.formatter.format(self.input_str)
        self.assertIsNotNone(
            result,
            "Formatter succeeded")
        self.assertListEqual(
            result,
            self.input_answer,
            'Formater returned the correct list')
        for (index, item) in enumerate(result):
            self.assertDictEqual(
                item,
                self.input_answer[index],
                'Formatter created the correct dict (' + str(index) + ')'
                )

    def test_format_malformed_string(self):
        self.input_str = (
            '{"ss":[["Thu","7:30","Final",,"ATL","23","BAL","27",,,"56112",,'
            '"PRE2","2013"],["Thu","7:30","Final",,"DET","6","CLE","24",,,'
            '"56113",,"PRE2","2013"]]}')

        try:
            result = self.formatter.format(self.input_str)

            self.assertListEqual(result, [], 'Formatter returns an empty list')
        except JSONDecodeError:
            self.fail('JSONDecodeError not caught')

    def test_format_test_season(self):
        self.input_str = self.data_generator.generate_data(data_type='TST')

        self.input_answer = [
            {
                d.AWAY_NAME: "OAK",
                d.AWAY_SCORE: 20,
                d.GAME_CLOCK: "",
                d.GAME_DAY: "Fri",
                d.GAME_SEASON: 2013,
                d.GAME_STATUS: "Final",
                d.GAME_TAG: "PRE1234",
                d.GAME_TIME: "8:00",
                d.GAME_WEEK: 1234,
                d.HOME_NAME: "NO",
                d.HOME_SCORE: 28,
                d.NFL_GAME_ID: 56117
            },
            {
                d.AWAY_NAME: "DAL",
                d.AWAY_SCORE: 0,
                d.GAME_CLOCK: "",
                d.GAME_DAY: "Sat",
                d.GAME_SEASON: 2013,
                d.GAME_STATUS: "Pregame",
                d.GAME_TAG: "PRE1234",
                d.GAME_TIME: "4:30",
                d.GAME_WEEK: 1234,
                d.HOME_NAME: "ARI",
                d.HOME_SCORE: 0,
                d.NFL_GAME_ID: 56118
            }
        ]

        result = self.formatter.format(self.input_str)
        self.assertIsNotNone(
            result,
            "Formatter succeeded")
        self.assertListEqual(
            result,
            self.input_answer,
            'Formater returned the correct list')
        for (index, item) in enumerate(result):
            self.assertDictEqual(
                item,
                self.input_answer[index],
                'Formatter created the correct dict (' + str(index) + ')'
                )
