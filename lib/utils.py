from __future__ import unicode_literals

import datetime

from lib.constants import NFL as nfl

class Utils(object):
    @staticmethod
    def default_week():
        time_delta = datetime.datetime.now() - nfl.WEEK_ONE[nfl.YEAR]

        return (time_delta.days/7)+1