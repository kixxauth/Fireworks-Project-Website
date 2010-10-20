import logging

import utils
import base_handler
from werkzeug.exceptions import InternalServerError

NO_CACHE_HEADER = utils.NO_CACHE_HEADER
ON_DEV_SERVER   = utils.ON_DEV_SERVER
trace_out       = utils.trace_out

BaseHandler = base_handler.BaseHandler

# TODO: A more creative 404 response.
def not_found(handler, environ):
  """To be passed into the fwerks module to handle unmatched paths.

  We define the general 'not found' handler here for easy access to other tools
  in this module. This function is designed to be passed to the FWerks
  application constructor function in `request.py`.

  `response` A pre-constructed response object.
  """
  response = BaseHandler.set_default_headers(handler.get_response(environ))

  # We have to set all the headers using the header dictionary on the response
  # because the NotFound class does not have utility wrappers for them.
  response.headers['Expires'] = '-1'
  response.headers['Pragma'] = 'no-cache'
  response.headers['Cache-Control'] = NO_CACHE_HEADER
  response.headers['Content-Type'] = 'text/html; charset=utf-8'
  response.headers['Connection'] = 'close'
  return response

def request_redirect(handler, environ):
  """To be passed into the fwerks module to handle mis-matched paths.

  We define the general 'redirect' handler here for easy access to other tools
  in this module. This function is designed to be passed to the FWerks
  application constructor function in `request.py`.

  `response` A pre-constructed response object.
  """
  # There is no need to format a nice redirect response, since
  # browsers will automatically redirect
  response = BaseHandler.set_default_headers(handler.get_response(environ))

  # Expire in 4 weeks.
  response.headers['Expires'] = http_date(time.time() + (86400 * 28))
  response.headers['Cache-Control'] = 'public, max-age=%d' % (86400 * 28)
  response.headers['Connection'] = 'close'
  return response


# TODO: A more creative 500 response.
def exception_handler(exception, env):
  """To be passed into the fwerks module for general exception handling.

  We define the general exception handling function here for easy access to
  other tools in this module. This function is designed to be passed to the
  FWerks application constructor function in `request.py`.

  `exception` is the exception object that was caught.
  `request` is a Werkzeug request object.
  `out` is a callable used to create a Werkzeug response object.
  """
  logging.exception(exception)
  response = InternalServerError()
  if ON_DEV_SERVER:
    response.description = '<pre>%s</pre>'% trace_out()
  return response
