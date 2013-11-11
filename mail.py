#! /usr/bin/env python

import datetime
import string
import email
import logging
try: import simplejson as json
except ImportError: import json

from lxml import html
from lxml.html.clean import Cleaner
from collections import deque

from lib.constants import NFL as nfl
from lib.secrets import SECRETS as s

from google.appengine.api import mail
from google.appengine.ext import webapp

from models.score import ScoreFactory
from models.spread import SpreadFactory

from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 
from google.appengine.ext.webapp.util import run_wsgi_app

class ReceiveMail(InboundMailHandler):
    """
    """

    def receive(self, message):
        """Event that is fired upon receiving an email

        """
        data = self._parse(message)

        if len(data) > 0:
            spread = SpreadFactory().get_instance()
            spread.save(self._default_week(), data)
            self._success(message.subject, data)
            #self._ping(message.subject, data)
        
    def _parse(self, message):
        htmltext = message.bodies('text/html')
        player_picks = {}
        stripped = ''
        tree = None
        tables = None
        cleaner = Cleaner(style=True,
                          links=True,
                          page_structure=True,
                          javascript=True,
                          scripts=True,
                          remove_tags=(['font','div', 'u', 'b', 'i']))
        result = []

        for content_type, body in htmltext:
            decoded = body.decode()

            tree = self._filter_and_transform_to_tree(decoded)

            tables = tree.xpath('//tbody')
            for page in tables:
                spread_data = []

                for row in cleaner.clean_html(page):
                    cell_row_data = self._extract_elements_from_tr(row)

                    if len(cell_row_data) > 2:
                        spread_data.append(cell_row_data)
                    elif len(cell_row_data) > 0 and 'DEFAULT' in cell_row_data[0]:
                        spread_data.append(cell_row_data)
                    elif len(spread_data) > 0 and 'page' in cell_row_data[0]:
                        # Came across a new page within the same table
                        # Treat it like we're at the end of a page
                        player_picks.update(self._organize_spread_data_page(spread_data))
                        spread_data = []


                player_picks.update(self._organize_spread_data_page(spread_data))


        for name, pick in self._convert_to_id_table(player_picks).iteritems():
            result.append(self._convert_to_spread_object(name, pick))

        return result



    def _organize_spread_data_page(self, spread_data):
        LABEL = {
            "HEADER": 'Name'
        }
        header = []
        width = 0
        result = {}
        working = deque(spread_data)

        # Drop miscellaneous "Page" data
        try:
            if working[0] is not None and working[0][0] is not None:
                if 'page' in working[0][0]:
                    working.popleft()
        except IndexError:
            logging.error('IndexError')
            logging.error(working)
            return result
        
        # header is always the first line
        header = working.popleft()[1:]
        # Initialize dict
        for name in header:
            result[name] = []
            width += 1

        # Remove the 3 rows of season-long header information
        #    Info includes last week's points & total season points
        # XXX: assumes the header information is constant
        for i in range(0,3):
            working.popleft()

        for row in working:
            if len(row) < width:
                continue

            current = deque(row)
            # Shift the extraneous data
            while len(current) > width:
                current.popleft()

            for name in header:
                result[name].append(current.popleft())

        return result

    def _convert_to_id_table(self, player_picks):
        mapping = self._get_game_ids_map()
        result = {}
        picks = []

        for player_name in player_picks:
            picks = deque(player_picks[player_name])
            canary = 1000

            result[player_name] = {}
            while len(picks) > 0 and canary > 0:
                item = []
                # get the game data
                if len(picks) > 2:
                    try:
                        float(picks[2])

                        # Spread, Over/Under, & Total Score
                        for i in range(0,3):
                            item.append(picks.popleft())
                    except ValueError:
                        # Single-game pick
                        item.append(picks.popleft())
                else:
                    item.append(picks.popleft())

                # Guard against scratched picks
                if item[0] != 'X' and item[0] != 'x':
                    # match to id
                    try:
                        game_id = unicode(mapping[item[0]])
                    except KeyError:
                        logging.error('KeyError during mapping')
                        logging.error(player_name)
                        logging.error(player_picks)

                        self._ping('Error Received', {
                                "Player Name": player_name,
                                "Player Picks": picks
                            });

                        # Bail from error
                        return []

                    # Save
                    result[player_name][game_id] = item

                canary -= 1

        return result

    def _get_game_ids_map(self):
        score_factory = ScoreFactory().get_instance(depth=4)
        scores = score_factory.fetch(self._default_week())
        #inital_map = dict((v,k) for k,v in nfl.TEAM_NAME.iteritems())
        result = {}

        for game in scores:
            result[game['home_name']] = game['game_id']
            result[game['away_name']] = game['game_id']

        # Workaround for arizona
        if 'ARI' in result:
            result['AZ'] = result['ARI']

        return result

    def _filter_and_transform_to_tree(self, html_string):
        # Filter out newlines, tabs, return carriages, and '*' characters
        trans_table = string.maketrans('\n\t\r*', '    ')
        stripped = html_string.encode('utf-8').translate(trans_table)

        # Load html tree & grab the tables
        return html.fromstring(stripped)

    def _extract_elements_from_tr(self, row):
        transform = lambda x: x.text.strip()
        condition = lambda x: x.text != None and len(x.text.strip()) > 0 and '/' not in x.text and '-' not in x.text

        return [transform(x) for x in row if condition(x)]

    def _convert_to_spread_object(self, owner_name, spread_data):
        result = {
            'year': nfl.YEAR,
            'week': self._default_week(),
            'owner': owner_name
        }

        for game_id, picks in spread_data.iteritems():
            result[game_id] = picks

        return result

    def _default_week(self):
        time_delta = datetime.datetime.now() - nfl.WEEK_ONE[nfl.YEAR]
        current_week = (time_delta.days/7)+1

        if current_week <= 0:
            # Preseason
            time_delta = datetime.datetime.now() - nfl.PRE_WEEK_ONE[nfl.YEAR]
            current_week = (time_delta.days/7)+1
        elif current_week > 17:
            current_week = current_week
        else:
            current_week = current_week

        return current_week

    def _ping(self, subject, spread_data):
        """
        Sends an email
        """
        if subject == None or len(subject) == 0:
            subject = 'OG FOOTBALL LEAGUE'

        message_ping = mail.EmailMessage(
                sender=s.EMAIL_SENDER,
                subject=subject)

        message_ping.to = s.EMAIL_TARGET
        message_ping.body = """
                            Reclaimer,

                            This is our response to your challenge.

                            """
        message_ping.body += json.dumps(spread_data, indent = 4)
        message_ping.body += "\n\n" + '-- Arbiter'

        message_ping.send()

    def _success(self, subject, spread_data):
        """
        Sends an email
        """
        if subject == None or len(subject) == 0:
            subject = 'OG FOOTBALL LEAGUE'

        message_ping = mail.EmailMessage(
                sender=s.EMAIL_SENDER,
                subject=subject)

        message_ping.to = s.EMAIL_TARGET
        message_ping.body = """
                            Reclaimer,

                            This is our notification that the spread was processed and saved.


                            -- Arbiter
                            """

        message_ping.send()

application = webapp.WSGIApplication([
    ReceiveMail.mapping()
], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
