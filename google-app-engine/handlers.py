"""
  FWPWebsite.handlers
  ~~~~~~~~~~~~~~~~~~~
  WSGI application request handlers for FWerks (see fwerks.py for more info)

  :copyright: (c) 2010 by The Fireworks Project.
  :license: MIT, see LICENSE for more details.
"""

import os
import time
import logging

from fwerks import Handler
import utils
from werkzeug.exceptions import NotFound, InternalServerError

# Standard 'Do not cache this!' declaration for the cache-control header.
NO_CACHE_HEADER = 'no-cache, no-store, must-revalidate, pre-check=0, post-check=0'

# Determine if we are running locally or not.
ON_DEV_SERVER = os.environ['SERVER_SOFTWARE'].startswith('Development')

def set_default_headers(response):
  """Utility shortcut available to quickly set some default headers.
  """
  # We don't want IE munging our response, so we set
  # X-XSS-Protection to 0
  response.headers['X-XSS-Protection'] = '0'
  return response

def exception_handler(exception, request, out):
  """To be passed into the fwerks module.

  We define the general exception handling function here for easy access to
  other tools in this module.
  """
  logging.exception(exception)
  if ON_DEV_SERVER:
    response = out(utils.trace_out())
    response.status_code = 500
  else:
    # TODO: A nice 500 response.
    response = InternalServerError()
  return response

def not_found(request, out):
  """To be passed into the fwerks module.

  We define the general 'not found' handler here for easy access to
  other tools in this module.
  """
  # TODO: A nice 404 response.
  response = set_default_headers(NotFound().get_response(request.environ))

  # We have to set all the headers using the header dictionary on the response
  # because the NotFound class does not have utility wrappers for them.
  response.headers['Expires'] = '-1'
  response.headers['Pragma'] = 'no-cache'
  response.headers['Cache-Control'] = NO_CACHE_HEADER
  response.headers['Content-Type'] = 'text/html; charset=utf-8'
  response.headers['Connection'] = 'close'
  return response

class SimpleHandler(Handler):
  """General request handling class for most of the requests we get.

  This class is designed and written to be used by the fwerks module.
  It handles typical GET and HEAD requests.
  """
  # Default template name.
  template = 'home'

  # Default template context object.
  context = {
      'taglines': [
        'For big ideas.',
        'Dream big.',
        'Dream different.',
        'Simply more productive.',
        'Simply uncomplicated.',
        'Sheer simplicity.']
      }

  # Prepare and send the response.
  def respond(self):
    response = set_default_headers(
        self.out(
          utils.render_template(self.template, self.context)))
    response.mimetype = 'text/html'
    response.add_etag()

    # Expire in 4 days.
    response.expires = time.time() + (86400 * 4)
    response.headers['Cache-Control'] = 'public, max-age=%d' % (86400 * 4)

    return response.make_conditional(self.request)

  def get(self):
    """Accept the HTTP GET method."""
    return self.respond()

  def head(self):
    """Accept the HTTP HEAD method."""
    return self.respond()

class IndexHandler(SimpleHandler):
  """Handler class for '/' URL."""
  template = 'home'

class JoinHandler(SimpleHandler):
  """Handler class for '/join' URL."""
  template = 'join'

class ProjectsHandler(SimpleHandler):
  """Handler class for '/projects' URL."""
  template = 'projects'

class TestException(Handler):
  """Handler class for '/exception' URL.

  Designed to be used to test how the live server responds in the case of an
  exception.
  """
  def get(self):
    assert False, 'Test Exception Raised!'


# Create the handler map for export to the request handling script.  As you can
# see, the map is a list of tuples. The first item in each tuple is the URL
# path for Werkzeug to match. The second item in each tuple is the name if the
# endpoint for Werkzeug. The third item in each tuple is a reference to the
# handler class for the fwerks module to use.
handler_map = [('/', 'index', IndexHandler)
    , ('/projects', 'projects', ProjectsHandler)
    , ('/projects/', 'projects', ProjectsHandler)
    , ('/join', 'join', JoinHandler)
    , ('/exception', 'exception', TestException)
    ]

