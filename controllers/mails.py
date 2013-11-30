#! /usr/bin/env python

import datetime
import string
import logging
try: import simplejson as json
except ImportError: import json

from lxml import html
from lxml.html.clean import Cleaner
from collections import deque

from lib.utils import Utils as utils

from google.appengine.api import mail
from google.appengine.ext import webapp

from models.score import ScoreFactory
from models.spread import SpreadFactory

from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 
from google.appengine.ext.webapp.util import run_wsgi_app

class ReceiveMail(InboundMailHandler):
    __SENDER = ''

    """
    """

    def receive(self, message):
        """Event that is fired upon receiving an email

        """
        result = {}

        try:
            spread_data = self._parse_for_spread_data(message)
            player_picks = self._map_data_to_dict(spread_data)

            result = self._convert_to_id_table(player_picks)
        except:
            result = {
                'error': 'An error was received :('
            }

        if len(result) > 0:
            spread = SpreadFactory().get_instance()
            spread.save(utils.default_week(), result)
            self._success(message.to, message.sender, message.subject, result)

        
    def _parse_for_spread_data(self, message):
        htmltext = message.bodies('text/html')
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

                    if len(cell_row_data) > 1:
                        if 'DEFAULT PICK' in cell_row_data[0] or 'POINTS' in cell_row_data[0]:
                            # no one cares about season meta-data
                            pass
                        elif 'Name' in cell_row_data[0] and len(spread_data) > 0:
                            # Came across a new page
                            result.append(spread_data)

                            # Reset the spread_data before saving to it again
                            spread_data = []
                            spread_data.append(cell_row_data)
                        else:
                            spread_data.append(cell_row_data)


                result.append(spread_data)
                spread_data = []

        return result

    def _map_data_to_dict(self, spread_data):
        result = {}

        for page in spread_data:
            width = 0
            current = {}

            for row in page:
                working = deque(row)

                # Check if working with header
                if 'Name' in working[0]:
                    #drop meta-header
                    working.popleft()

                    # Save header data as keys
                    while len(working) > 0:
                        name = working.popleft()

                        # Guard against placeholder columns
                        if 'X' != name and 'x' != name:
                            current[name] = []
                            width += 1
                else:
                    while len(working) > width:
                        # remove extraneous data from right-end of row
                        working.pop()

                    for player in current:
                        current[player].append(working.popleft())

            # combine current with final result
            result.update(current)

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
        scores = score_factory.fetch(utils.default_week())
        result = {}

        for game in scores:
            result[game['home_name']] = game['game_id']
            result[game['away_name']] = game['game_id']

        # Workaround for arizona
        # TODO: in wrong place; should trust source of truth
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


    def _success(self, email_sender, email_target, subject, spread_data):
        """
        Sends an email
        """
        if subject == None or len(subject) == 0:
            subject = 'OG FOOTBALL LEAGUE'

        message_ping = mail.EmailMessage(
                sender=email_sender,
                subject=subject)

        message_ping.to = email_target
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
