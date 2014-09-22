import json
import webapp2

from controllers.v1 import status
from webapp2_extras import routes



application = webapp2.WSGIApplication([
        routes.PathPrefixRoute('/api/v1', [
            webapp2.Route('/status', status.StatusPage)
        ])
    ], debug=True)