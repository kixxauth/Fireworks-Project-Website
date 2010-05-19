import re
import httplib

# The current host name we're testing on.
HOST = None

# True if we're running on the localhost:8080 dev_appserver.
# False if not.
LOCAL = True

# If you don't know what this is you need to read the HTTP spec.
# http://tools.ietf.org/html/rfc2616#section-9
METHODS = ['GET','POST','PUT','DELETE','OPTIONS','HEAD','TRACE']

# This is a set of request headers that mimic a web browser.
# Again, if you don't know what a header is you should read the HTTP spec.
# http://tools.ietf.org/html/rfc2616#section-14
#
# TODO: Test other browsers. (This is Firefox 3.6.3)
BROWSER_HEADERS = dict([
    ('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3'),
    ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
    # TODO: Test other languages.
    ('Accept-Language', 'en-us,en;q=0.5'),
    ('Accept-Encoding', 'gzip,deflate'),
    ('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'),
    ('Keep-Alive', '115'),
    ('Connection', 'keep-alive'),
    ('Pragma', 'no-cache'),
    ('Cache-Control', 'no-cache')
  ])

# This is a regex for testing the correctness of an HTTP date field like
# in a Date or Expiration header.
HTTP_DATE_RX = re.compile('^[SMTWF]{1}[unoedhriat]{2}, [0-3]{1}[0-9]{1} [JFMASOND]{1}[anebrpyulgctov]{2} 20[0-9]{2} [012]{1}[0-9]{1}:[0-5]{1}[0-9]{1}:[0-5]{1}[0-9]{1} GMT$')

# This is the header our server uses to say "Everbody listen up! Don't cache
# this resource!" We assign it to a variable name here so we don't have to type
# it out all over the place.
NO_CACHE_HEADER = 'no-cache, no-store, must-revalidate, pre-check=0, post-check=0'

def update_browser_headers(new_headers=None):
  """Make a copy of the standard browser headers dict and update it before
  returning it.
  """
  headers = dict(BROWSER_HEADERS)
  if isinstance(new_headers, list):
    headers.update(new_headers)
  return headers

def make_fake_body(method=None):
  """Create a return a string to make a fake body for a request.
  
  If `method` is given it should be one of the HTTP method names as an
  uppercase string. If it is 'PUT' or 'POST' or None, a string is returned that
  is suitable for use as a request with content type
  `application/x-www-form-urlencoded`,
  """
  body = 'k=tfp&num=44'
  if method != None:
    return (method == 'POST' or method == 'PUT') and body or None

def check_headers(test, response, headers, msg=''):
  """Iterate through a list of headers, testing each one.

  `test` Should be the test object.
  `response` Should be an instance of Response.
  `headers` Should be a list of tuples of the form
    (directive, header name, expected value)
    where directive may be 'eq', 'regex', or 'len'.
  `msg` Should be a message string to append on the end of the failure message.
  """
  for type, k, expected_value in headers:
    value = response.headers.get(k)
    if type == 'regex':
      assert expected_value.match(value), \
          ('header %s: %s ; does not match regex %s; %s' %
              (k, value, expected_value, msg))
      continue
    if type == 'len':
      value = len(value)
    test.assertEqual(value, expected_value,
        "header '%s' is %s; %s" % (k, value, msg))

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

def setup(host, local):
  """Global setup function called by testrunner.py"""
  global HOST
  global LOCAL

  HOST = host
  LOCAL = local
  BROWSER_HEADERS.update([('Host', HOST)])

