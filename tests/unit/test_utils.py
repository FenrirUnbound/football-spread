#! /usr/bin/env python
from __future__ import unicode_literals

import datetime
import unittest

from lib.constants import NFL as nfl
from lib.utils import Utils as utils

class TestUtils(unittest.TestCase):
    def test_default_week(self):
        time_delta = datetime.datetime.now() - nfl.WEEK_ONE[nfl.YEAR]
        current_week = (time_delta.days/7)+1

        week = utils.default_week()
        self.assertEqual(current_week, week)