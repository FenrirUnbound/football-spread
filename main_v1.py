import json
import webapp2

from webapp2_extras import routes

class StatusPage(webapp2.RequestHandler):
    def get(self):
        result = { 'status': 'OK'}

        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.write(json.dumps(result, indent = 4))


application = webapp2.WSGIApplication([
        routes.PathPrefixRoute('/api/v1', [
            webapp2.Route('/status', StatusPage)
        ])
    ], debug=True)