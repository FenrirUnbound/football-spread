"""

Help from:
* https://github.com/crhym3/simpleauth/blob/master/tests/__init__.py
* https://gist.github.com/kesor/1179782
"""
from __future__ import unicode_literals

from google.appengine.api import apiproxy_stub
from google.appengine.api import apiproxy_stub_map
from google.appengine.api import urlfetch
from google.appengine.api import urlfetch_service_pb

class UrlFetchMock(apiproxy_stub.APIProxyStub):
    def __init__(self, service_name="urlfetch"):
        super(UrlFetchMock, self).__init__(service_name=service_name)

    def set_return_values(self, **kwargs):
        self.return_values = kwargs

    def _Dynamic_Fetch(self, request, response):
        print 'top'

        if not hasattr(self, 'return_values'):
            print dir(self)
        return_values = getattr(self, 'return_values')

        response.set_content(return_values.get('content', ''))
        response.set_statuscode(return_values.get('status_code', 500))

        for header_key, header_value in return_values.get('headers', {}).iteritems():
            new_header = response.add_header()
            new_header.set_key(header_key)
            new_header.set_value(header_value)
        response.set_finalurl(return_values.get('final_url', request.url()))
        response.set_contentwastruncated(return_values.get('content_was_truncated', False))

        return _UrlFetchBlob(response)


class _UrlFetchBlob(object):
  """A Pythonic representation of our fetch response protocol buffer.
  """

  def __init__(self, response_proto):
    """Constructor.

    Args:
      response_proto: the URLFetchResponse proto buffer to wrap.

      self.header_msg = httplib.HTTPMessage(
        StringIO.StringIO(''.join(['%s: %s\n' % (h.key(), h.value())
                          for h in response_proto.header_list()] + ['\n'])))
    """
    self.__pb = response_proto
    self.content = response_proto.content()
    self.status_code = response_proto.statuscode()
    self.content_was_truncated = response_proto.contentwastruncated()
    self.final_url = response_proto.finalurl() or None
    #self.header.msg = self.__construct_header_msg
    #self.headers = self.__construct_header_msg(response_proto.header_list())
