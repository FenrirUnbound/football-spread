#! /usr/bin/env python
from __future__ import unicode_literals

import unittest

from google.appengine.api import urlfetch
from google.appengine.api import urlfetch_service_pb
from google.appengine.ext import testbed

from lib.constants import SCOREBOARD as sb
from test_lib.mock_service import UrlFetchMock
from test_lib.mock_service import _UrlFetchBlob as UrlFetchBlob


class TestMockService(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_urlfetch_stub()

        self.fetch_mock = UrlFetchMock()
        self.testbed._register_stub(testbed.URLFETCH_SERVICE_NAME, self.fetch_mock)

    def tearDown(self):
        self.testbed.deactivate()

    def test_create_instance(self):
        mock_service = UrlFetchMock()
        self.assertIsNotNone(
            mock_service,
            "Not none")

    def test_create_rpc(self):
        rpc = urlfetch.create_rpc()
        self.assertIsNotNone(
            rpc,
            "RPC Creation")

    def test_make_fetch_call(self):
        data = {
            "status_code": 200,
            "content": "success"
        }
        self.fetch_mock.set_return_values(**data)

        rpc = urlfetch.create_rpc()
        urlfetch.make_fetch_call(rpc, "http://www.fakeashell.com")

        response = rpc.get_result()
        self.assertEquals(
            response.status_code,
            data['status_code'],
            "Status code 200 OK")
        self.assertEquals(
            response.content,
            data['content'],
            "Status code 200 OK")

    def test_make_fetch_call_fake_server_error(self):
        data = {
            "status_code": 502,
            "content": "Bad Gateway dude"
        }
        self.fetch_mock.set_return_values(**data)

        rpc = urlfetch.create_rpc()
        urlfetch.make_fetch_call(rpc, "http://www.fakeashell.com")

        response = rpc.get_result()
        self.assertEquals(
            response.status_code,
            data['status_code'],
            "Status code 200 OK")
        self.assertEquals(
            response.content,
            data['content'],
            "Status code 200 OK")

class Test_UrlFetchBlob(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_instance(self):
        content = "There is no place like home."
        content_was_truncated = False
        final_url = "http://www.somethingbogus.com/isUpThere"
        item = None
        status_code = 420

        response = urlfetch_service_pb.URLFetchResponse()
        response.set_content(content)
        response.set_statuscode(status_code)
        response.set_contentwastruncated(content_was_truncated)
        response.set_finalurl(final_url)

        item = UrlFetchBlob(response)
        self.assertIsNotNone(
            item,
            "Item created")

        self.assertEquals(
            item.content,
            content,
            "Content matches")
        self.assertEquals(
            item.status_code,
            status_code,
            "Status code matches")
        self.assertEquals(
            item.content_was_truncated,
            content_was_truncated,
            "Content_Truncated flag matches")
        self.assertEquals(
            item.final_url,
            final_url,
            "Final URL matches")