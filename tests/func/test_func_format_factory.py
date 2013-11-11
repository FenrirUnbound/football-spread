#! /usr/bin/env python

from __future__ import unicode_literals

import unittest

from lib.constants import DATA_BLOB as d
from lib.constants import NFL as nfl

from models.format_scores import FormatFactory

class TestFormatFactory(unittest.TestCase):
    def setUp(self):
        self.input_post_season = (
            u'{"ss":[["Sat","4:30","final overtime",,"Baltimore Ravens",'
            '"BAL","38","Denver Broncos","DEN","35",,,"55829",,"CBS",'
            '"POST22","2012"]]}')
        self.input_reg_season = (
            u'{"ss":[["Sat","4:30","final overtime",,"BAL",'
            '"38","DEN","35",,,"55829",,"REG11","2012"]]}')

        self.formatter = FormatFactory().get_instance()

    def tearDown(self):
        pass

    def test_get_instance(self):
        self.assertIsNotNone(
            self.formatter,
            "Received instance from formatter factory")

    def test_format_post_season(self):
        result = self.formatter.format(self.input_post_season)
        self.input_answer = [
            {
                d.AWAY_NAME: "BAL",
                d.AWAY_SCORE: 38,
                d.GAME_CLOCK: "",
                d.GAME_DAY: "Sat",
                d.GAME_SEASON: 2012,
                d.GAME_STATUS: "Final Overtime",
                d.GAME_TAG: "POST22",
                d.GAME_TIME: "4:30",
                d.GAME_WEEK: 22 + nfl.WEEK_PREFIX['POS'],
                d.HOME_NAME: "DEN",
                d.HOME_SCORE: 35,
                d.NFL_GAME_ID: 55829
            }
        ]

        self.assertEqual(
            result,
            self.input_answer,
            "Scores were properly formatted")

    def test_format_reg_season(self):
        result = self.formatter.format(self.input_reg_season)
        self.input_answer = [
            {
                d.AWAY_NAME: "BAL",
                d.AWAY_SCORE: 38,
                d.GAME_CLOCK: "",
                d.GAME_DAY: "Sat",
                d.GAME_SEASON: 2012,
                d.GAME_STATUS: "Final Overtime",
                d.GAME_TAG: "REG11",
                d.GAME_TIME: "4:30",
                d.GAME_WEEK: 11 + nfl.WEEK_PREFIX['REG'],
                d.HOME_NAME: "DEN",
                d.HOME_SCORE: 35,
                d.NFL_GAME_ID: 55829
            }
        ]

        self.assertEqual(
            result,
            self.input_answer,
            "Scores were properly formatted")