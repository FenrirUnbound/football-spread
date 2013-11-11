from __future__ import unicode_literals

import datetime
import unittest

from test_lib.testdata_factory import TestDataFactory

class TestTestDataFactory(unittest.TestCase):
    def setUp(self):
        self.factory = TestDataFactory()
        self.timestamp = int(datetime.datetime.now().strftime('%s'))

    def test_initialization(self):
        factory = TestDataFactory()

        self.assertIsNotNone(
            factory,
            "Factory is not None")

    def test_get_instance_default_is_timestamp(self):
        data = self.factory.get_instance()

        self.assertTrue(
            self.timestamp <= data,
            "Timestamp is accurate enough")

    def test_get_instance_timestamp(self):
        data = self.factory.get_instance("timestamp")

        self.assertTrue(
            self.timestamp <= data,
            "Timestamp is accurate enough")

    def test_get_instance_week(self):
        data = self.factory.get_instance("week")

        self.assertTrue(
            (data >= 50) and (data <= 1050),
            "Generated week is within tolerable ranges") 