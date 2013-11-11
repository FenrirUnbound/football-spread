from __future__ import unicode_literals

import datetime

class TestDataFactory(object):
    def get_instance(self, data_type="timestamp"):
        result = {
            "timestamp": self._timestamp(),
            "week": self._week()
        } [data_type]

        return result

    def _timestamp(self):
        return int(datetime.datetime.now().strftime('%s'))

    def _week(self):
        return (self._timestamp() % 1000) + 50