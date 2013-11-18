import webapp2

from controllers import scores, spreads

from google.appengine.ext.webapp import util

def main():
    appplication = get_app()

    util.run_wsgi_app(application)

def get_app():
    application = webapp2.WSGIApplication([
            ('/scores', scores.ScoresHandler),
            ('/scores/(.*)', scores.ScoresHandler),
            ('/spreads', spreads.SpreadsHandler)
        ], debug=True)

    return application

if __name__ == "__main__":
    main()