import logging

from fwerks import Handler
from config import on_dev_server
from utils import trace_out
from werkzeug.exceptions import NotFound, InternalServerError

NO_CACHE_HEADER = 'no-cache, no-store, must-revalidate, pre-check=0, post-check=0'

def set_default_headers(response):
  # We don't want IE munging our response, so we set
  # X-XSS-Protection to 0
  response.headers['X-XSS-Protection'] = '0'
  return response

def not_found(request, out):
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
  

def exception_handler(exception, request, out):
  logging.exception(exception)
  if on_dev_server:
    response = out(trace_out())
    response.status_code = 500
  else:
    # TODO: A nice 500 response.
    response = InternalServerError()
  return response

class IndexHandler(Handler):
  def get(self):
    return self.out('Hello World!')

class TestException(Handler):
  def get(self):
    assert False, 'Test Exception Raised!'

handler_map = [('/', 'index', IndexHandler)
    , ('/exception', 'exception', TestException)
    ]

