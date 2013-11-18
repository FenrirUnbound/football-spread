from __future__ import unicode_literals

try: 
    import simplejson as json
    from simplejson import JSONDecodeError
except ImportError:
    import json

import logging

from lib.constants import CONSTANTS as c
from lib.constants import DATA_BLOB as d
from lib.constants import SCOREBOARD as sb
from lib.constants import NFL as nfl

class FormatFactory():
    def get_instance(self):
        return self._create_instance()

    def _create_instance(self):
        return _FormatPadding(
            _FormatOvertime(
                _FormatUnicode(
                    _FormatMapper(None))))

class Formatter(object):
    def __init__(self, nextFormatter=None):
        self.next = nextFormatter

    def format(self, input_str):
        result = self._format(input_str)

        if self.next != None:
            return self.next.format(result)
        else:
            return result

    def _format(self, input_str):
        raise NotImplementedError("Subclasses should implement this")

class _FormatMapper(Formatter):
    __TEST_WEEK_THRESHOLD = 100

    """
    This is a terminating decorator
    """
    def __init__(self, nextFormatter=None):
        super(_FormatMapper, self).__init__(nextFormatter=None)

    def _format(self, input_str):
        scores = []
        result = []

        if not input_str:
            return input_str

        try:
            scores = (json.loads(input_str))[sb.SCOREBOARD_DATA]
        except:
            logging.error('Error processing score data')
            return result

        for game in scores:
            game_tag = game[-2][:3]
            week_prefix = nfl.WEEK_PREFIX[game_tag]

            # Check if post-season
            if "POS" == game_tag:
                week = ''.join(i for i in game[sb.POST_GAME_TAG] if i.isdigit())
                result.append( {
                    d.AWAY_NAME: game[sb.POST_AWAY_NAME] or "",
                    d.AWAY_SCORE: int(game[sb.POST_AWAY_SCORE]) or 0,
                    d.GAME_CLOCK: game[sb.POST_GAME_CLOCK] or "",
                    d.GAME_DAY: game[sb.POST_GAME_DAY] or "",
                    d.GAME_SEASON: int(game[sb.POST_GAME_SEASON]) or 0,
                    d.GAME_STATUS: game[sb.POST_GAME_STATUS] or "",
                    d.GAME_TAG: game[sb.POST_GAME_TAG],
                    d.GAME_TIME: game[sb.POST_GAME_TIME] or "",
                    d.GAME_WEEK: (int(week) or 0) + week_prefix,
                    d.HOME_NAME: game[sb.POST_HOME_NAME] or "",
                    d.HOME_SCORE: int(game[sb.POST_HOME_SCORE]) or 0,
                    d.NFL_GAME_ID: int(game[sb.POST_NFL_GAME_ID]) or 0
                    } )
            else:
                # Regular or Preseason
                week = ''.join(i for i in game[sb.REG_GAME_TAG] if i.isdigit())
                week = int(week) or 0
                week_prefix = week_prefix if week < _FormatMapper.__TEST_WEEK_THRESHOLD else 0

                result.append( {
                    d.AWAY_NAME: game[sb.REG_AWAY_NAME] or "",
                    d.AWAY_SCORE: int(game[sb.REG_AWAY_SCORE]) or 0,
                    d.GAME_CLOCK: game[sb.REG_GAME_CLOCK] or "",
                    d.GAME_DAY: game[sb.REG_GAME_DAY] or "",
                    d.GAME_SEASON: int(game[sb.REG_GAME_SEASON]) or 0,
                    d.GAME_STATUS: game[sb.REG_GAME_STATUS] or "",
                    d.GAME_TAG: game[sb.REG_GAME_TAG] or "",
                    d.GAME_TIME: game[sb.REG_GAME_TIME] or "",
                    d.GAME_WEEK: week + week_prefix,
                    d.HOME_NAME: game[sb.REG_HOME_NAME] or "",
                    d.HOME_SCORE: int(game[sb.REG_HOME_SCORE]) or 0,
                    d.NFL_GAME_ID: int(game[sb.REG_NFL_GAME_ID]) or 0
                    } )

        return result

class _FormatOvertime(Formatter):
    def __init__(self, nextFormatter=None):
        super(_FormatOvertime, self).__init__(nextFormatter=nextFormatter)

    def _format(self, input_str):
        return input_str.replace("final overtime", "Final Overtime")

class _FormatPadding(Formatter):
    __MAX_ITERATIONS = 100

    def __init__(self, nextFormatter=None):
        super(_FormatPadding, self).__init__(nextFormatter=nextFormatter)

    def _format(self, input_str):
        canary = _FormatPadding.__MAX_ITERATIONS
        result = input_str
        length = 0

        while length != len(result):
            length = len(result)
            result = result.replace(",,", ",0,")

            # Prevent infinite loops
            if canary > 0:
                canary -= 1
            else:
                break

        return result

class _FormatUnicode(Formatter):
    def __init__(self, nextFormatter=None):
        # No nextFormatter since this class is a terminator
        super(_FormatUnicode, self).__init__(nextFormatter=nextFormatter)

    def _format(self, input_str):
        if isinstance(input_str, basestring):
            if not isinstance(input_str, unicode):
                return unicode(input_str, c.ENCODING)

        return input_str
