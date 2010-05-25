"""
  FWPWebsite.request
  ~~~~~~~~~~~~~~~~~~
  WSGI application bootstrap for FWerks handlers.
  (see handlers.py for more info)

  :copyright: (c) 2010 by The Fireworks Project.
  :license: MIT, see LICENSE for more details.
"""

from fwerks import App
from google.appengine.ext.webapp.util import run_bare_wsgi_app
from handlers import handler_map, exception_handler, not_found

# Create a fwerks application object. Fwerks is our quick and dirty WSGI
# framework built with Werkzeug.
fireworks_project_website = App(handler_map, exception_handler, not_found)

def main():
  # Use GAE helper function to run the WSGI app.
  run_bare_wsgi_app(fireworks_project_website)

if __name__ == "__main__":
  main()

