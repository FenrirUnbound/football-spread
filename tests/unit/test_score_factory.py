#!/usr/bin/env python
from __future__ import unicode_literals

import unittest

from models.score import ScoreFactory
from models.score import Score
from models.score import _ScoreDatastore
from models.score import _ScoreMemcache
from models.score import _ScoreSource
from models.score import _ScoreFilter


class TestScoreFactory(unittest.TestCase):
    def setUp(self):
        self.factory = ScoreFactory()

    def tearDown(self):
        pass

    def test_get_instance(self):
        score = self.factory.get_instance()

        self.assertIsNotNone(
            score,
            "Factory creates a non-null object")

    def test_get_instance_is_Score(self):
        score = self.factory.get_instance()

        self.assertTrue(
            hasattr(score, 'fetch'),
            "Has public fetch")
        self.assertTrue(
            hasattr(score, 'save'),
            "Has public save")

    def test_depth_level(self):
        """
        Validate the factory gives a different-length chain based
        on the depth level.
        """
        score = self.factory.get_instance(depth=4)

        self.assertIsNotNone(
            score.next,
            "Has a depth of 2")
        self.assertIsNotNone(
            score.next.next,
            "Has a depth of 3")
        self.assertIsNotNone(
            score.next.next.next,
            "Has a depth of 4")
        self.assertIsNone(
            score.next.next.next.next,
            "Doesn't have a depth of 5")

    def test_depth_level_high_value(self):
        """
        Validate the factory gives the max-length chain available when given
        a depth value greater than the max-length
        """
        score = self.factory.get_instance(depth=4)

        self.assertIsNotNone(
            score.next,
            "Has a depth of 2")
        self.assertIsNotNone(
            score.next.next,
            "Has a depth of 3")
        self.assertIsNotNone(
            score.next.next.next,
            "Has a depth of 4")
        self.assertIsNone(
            score.next.next.next.next,
            "Doesn't have a depth of 5")

    def test_depth_level_none(self):
        """
        Validate the factory gives a zero-length chain
        """
        score = self.factory.get_instance(depth=0)

        self.assertIsNone(
            score,
            "Has a depth of 0")

    def test_depth_level_one(self):
        """
        Validate the facotry gives a _ScoreMemcache given a depth of 1
        """
        score = self.factory.get_instance(depth=1)

        self.assertIsNotNone(
            score,
            "Received an object")
        self.assertTrue(
            isinstance(score, _ScoreMemcache),
            "An instance of ScoreMemcache" )
        self.assertIsNone(
            score.next,
            "Has a depth no greater than 1")

    def test_depth_level_two(self):
        """
        Validate the factory gives a chain length of 2
        """
        score = self.factory.get_instance(depth=2)

        self.assertTrue(
            issubclass(type(score), Score),
            "An object of type Score")
        self.assertTrue(
            isinstance(score, _ScoreMemcache),
            "An instance of ScoreMemcache")
        self.assertIsNotNone(
            score.next,
            "Has a depth of at least 2")
        self.assertIsNone(
            score.next.next,
            "Has a depth no greater than 2")
        self.assertTrue(
            isinstance(score.next, _ScoreDatastore),
            "ScoreDatastore is next in chain" )

    def test_depth_level_three(self):
        """
        Validate the factory gives a chain length of 3
        """
        score = self.factory.get_instance(depth=3)

        self.assertTrue(
            issubclass(type(score), Score),
            "An object of type Score")
        self.assertTrue(
            isinstance(score, _ScoreMemcache),
            "An instance of ScoreMemcache")
        self.assertIsNotNone(
            score.next,
            "Has a depth of at least 2")
        self.assertTrue(
            isinstance(score.next, _ScoreDatastore),
            "ScoreDatastore is next in chain" )
        self.assertIsNotNone(
            score.next.next,
            "Has a depth of at least 3")
        self.assertTrue(
            isinstance(score.next.next, _ScoreSource),
            "ScoreSource is next in chain" )
        self.assertIsNone(
            score.next.next.next,
            "Does not have a depth of 4")

    def test_depth_level_four(self):
        """
        Validate the factory gives a chain length of 4
        """
        score = self.factory.get_instance(depth=4)

        self.assertTrue(
            issubclass(type(score), Score),
            "An object of type Score")
        self.assertTrue(
            isinstance(score, _ScoreFilter),
            "An instance of ScoreFilter")
        self.assertIsNotNone(
            score.next,
            "Has a depth of at least 2")
        self.assertTrue(
            isinstance(score.next, _ScoreMemcache),
            "ScoreMemcache is next in chain" )
        self.assertIsNotNone(
            score.next.next,
            "Has a depth of at least 3")
        self.assertTrue(
            isinstance(score.next.next, _ScoreDatastore),
            "ScoreDatastore is next in chain" )
        self.assertIsNotNone(
            score.next.next.next,
            "Has a depth of at least 4")
        self.assertTrue(
            isinstance(score.next.next.next, _ScoreSource),
            "ScoreSource is next in chain" )
        self.assertIsNone(
            score.next.next.next.next,
            'Does not have a depth of 5')

