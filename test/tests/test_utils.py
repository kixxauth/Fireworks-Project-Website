import re
import httplib
import unittest

# The current host name we're testing on.
HOST = None

# True if we're running on the localhost:8080 dev_appserver.
# False if not.
LOCAL = True

def setup(host, local):
  """Global setup function called by testrunner.py"""
  global HOST
  global LOCAL

  HOST = host
  LOCAL = local

# If you don't know what this is you need to read the HTTP spec.
# http://tools.ietf.org/html/rfc2616#section-9
METHODS = ['GET','POST','PUT','DELETE','OPTIONS','HEAD','TRACE']

# This is a regex for testing the correctness of an HTTP date field like
# in a Date or Expiration header.
HTTP_DATE_RX = re.compile('^[SMTWF]{1}[unoedhriat]{2}, [0-3]{1}[0-9]{1} [JFMASOND]{1}[anebrpyulgctov]{2} 20[0-9]{2} [012]{1}[0-9]{1}:[0-5]{1}[0-9]{1}:[0-5]{1}[0-9]{1} GMT$')

# This is the header our server uses to say "Everbody listen up! Don't cache
# this resource!" We assign it to a variable name here so we don't have to type
# it out all over the place.
NO_CACHE_HEADER = 'no-cache, no-store, must-revalidate, pre-check=0, post-check=0'

def test_response_headers(test, response, headers, msg=''):
  """Iterate through a list of headers, testing each one.

  `test` Should be the test object.
  `response` Should be an instance of Response.
  `headers` Should be a list of tuples of the form
    (directive, header name, expected value)
    where directive may be 'eq', 'regex', or 'len'.
  `msg` Should be a message string to append on the end of the failure message.
  """
  for k, cmp, expected_value in headers:
    value = response.headers.get(k)
    if cmp == 'regex':
      assert expected_value.match(value), \
          ('header "%s: %s" does not match regex %s; in %s' %
              (k, value, expected_value, msg))
    elif cmp == 'len':
      test.assertEqual(len(value), expected_value,
          'header "%s: %s" length != %d; %s' % (k, value, expected_value, msg))
    else:
      test.assertEqual(value, expected_value,
            'header "%s: %s" != %s; %s' % (k, value, expected_value, msg))

class Response(object):
  """Object constructor utility used by make_http_request()
  """
  pass

def make_http_request(method='POST', url='/', body=None, headers={}):
  """Handy shortcut to use for making HTTP requests intead of using httplib
  directly.
  """
  cxn = httplib.HTTPConnection(HOST)
  cxn.request(method, url, body, headers)
  response = cxn.getresponse()
  rv = Response()
  rv.status = response.status
  rv.message = response.reason
  rv.headers = dict(response.getheaders())
  rv.body = response.read()
  cxn.close()
  return rv

class TestRequest(object):
  """Utility object constructor to make creating a test request object easier.
  """
  def __init__(self, parent=None):
    # If we're passed a parent object we copy it...
    if parent:
      self.headers = dict(parent.headers.items())
      if self.headers.get('Host'):
        self.headers['Host'] = HOST
      self.body = parent.body
      self.response_status = parent.response_status
      self.response_headers = list(parent.response_headers)
      self.response_body = parent.response_body

    # otherwise we create a new one.
    else:
      self.headers = {}
      self.body = ''
      self.response_status = 200
      self.response_headers = []
      self.response_body = True

class TestConfig(object):
  """Utility object constructor used to make test configuration easier.
  """
  def __init__(self, parent=None):
    if parent:
      self.configs = dict(parent.items())
    else:
      self.configs = {}

  def items(self):
    return self.configs.items()

  def update(self, item, request):
    self.configs[item] = request
    return self

def do_test(test, name, method, request):
  """Utility function used to make a request and test the response.
  """
  # Call the server.
  response = make_http_request(
      method=method,
      url=test.url,
      body=request.body,
      headers=request.headers)

  # Check the HTTP status.
  test.assertEqual(response.status, request.response_status,
      ('HTTP status %d is not %d in %s for method %s' %
        (response.status,
          request.response_status,
          name,
          method)))

  # Check all the response headers.
  test_response_headers(
      test,
      response,
      request.response_headers,
      'in %s for method %s' % (name, method))

  # Check the response body depending on the expected type.

  # None or False; we check to make sure there is no response body.
  if not request.response_body:
    assert response.body == '' or response.body is None, \
        ('response body is expected to be None in %s for method %s'%
          (name, method))

  # In the case of an integer we test for length.
  elif isinstance(request.response_body, int):
    test.assertEqual(len(response.body), request.response_body,
      ('response body length is %d but expected to be %d in %s for method %s' %
        (len(response.body),
          request.response_body,
          name,
          method)))

  # In the case of True, we just make sure the body was returned.
  elif request.response_body is True:
    assert response.body, \
      ('response body does not exist in %s for method %s' %
        (name, method))

  # Lastly we do a regex check.
  else:
    try:
      assert request.response_body.match(response.body), \
          ('response body did not match regex %s in %s for method %s' %
            (request.response_body.pattern, name, method))
    except AttributeError, e:
      raise Exception(
        '.response_body attribute was expected to be a regex in %s' % name)

def test_function(test_method):
  """Decorator used to make a method into a URL test function.
  """
  method = test_method.__name__.upper()
  constructor = test_method

  def test_method_replacement(test):
    if not getattr(test, 'issetup', None):
      test.configure()
      test.issetup = True

    requests = constructor(test)
    assert isinstance(requests, list), \
        '%s.%s() must return a list' % (test.__name__, method)

    for name, request in requests:
      do_test(test, name, method, request)

  test_method_replacement.__doc__ = test_method.__doc__
  return test_method_replacement

