from __future__ import unicode_literals

class GameFeedFactory():
    def generate_data(self, data_type='REG'):
        function_generator = {
            'PRE': self._preseason_feed,
            'POS': self._postseason_feed,
            'REG': self._regseason_feed,
            'TST': self._testseason_feed
        } [data_type]

        return function_generator()

    def _preseason_feed(self):
        result = (
            '{"ss":[["Fri","8:00","Final",0,"OAK","20","NO","28",0,0,"56117",'
            '0,"PRE2","2013"],["Sat","4:30","Pregame",0,"DAL",0,"ARI",0,0,0,'
            '"56118",0,"PRE2","2013"]]}')

        return result

    def _postseason_feed(self):
        result = (
            '{"ss":[["Sat","4:30","final overtime",0,"Baltimore Ravens",'
            '"BAL","38","Denver Broncos","DEN","35",0,0,"55829",0,"CBS",'
            '"POST22","2012"]]}')

        return result

    def _regseason_feed(self):
        result = (
            '{"ss":[["Fri","7:00","Final",0,"MIN","16","BUF","20",0,0,"56115",'
            '0,"REG11","2013"],["Fri","8:00","Final",0,"SF","15","KC","13",0,'
            '0,"56116",0,"REG11","2013"]]}')

        return result

    def _testseason_feed(self):
        result = (
            '{"ss":[["Fri","8:00","Final",0,"OAK","20","NO","28",0,0,"56117",'
            '0,"PRE1234","2013"],["Sat","4:30","Pregame",0,"DAL",0,"ARI",0,0,0,'
            '"56118",0,"PRE1234","2013"]]}')

        return result