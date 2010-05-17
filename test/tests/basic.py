import unittest
import test_utils

METHODS = ['GET','POST','PUT','DELETE','OPTIONS','HEAD','TRACE']

# TODO: Test other browsers. (This is Firefox 3.6.3)
BROWSER_HEADERS = dict([
    ('Host', test_utils.HOST),
    ('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3'),
    ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
    # TODO: Test other languages.
    ('Accept-Language', 'en-us,en;q=0.5'),
    ('Accept-Encoding', 'gzip,deflate'),
    ('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'),
    ('Keep-Alive', '115'),
    ('Connection', 'keep-alive'),
    ('Cache-Control', 'max-age=0')
  ])

def update_browser_headers(new_headers):
  headers = dict(BROWSER_HEADERS)
  headers.update(new_headers)
  return headers

def make_fake_body(method=None):
  body = 'k=tfp&num=44'
  if method != None:
    return (method == 'POST' or method == 'PUT') and body or None

def run_methods(mapping, function):
  for t in mapping:
    function(*t)

def check_headers(test, response, headers, msg=''):
  for type, k, expected_value in headers:
    value = response.headers.get(k)
    if type == 'len':
      value = len(value)
    test.assertEqual(value, expected_value,
        "header '%s' is %s; %s" % (k, value, msg))

class Defaults(unittest.TestCase):
  # TODO: favicon

  def test_notFound(self):
    """Check for not found response.
    """
    url = '/lost_city_of_atlantis'

    response_headers = [
        # TODO: Date header should be tested with a regex.
        ('len', 'date', 29),
        ('eq', 'expires', '-1'),
        ('eq', 'cache-control', 'no-cache, no-store, must-revalidate, pre-check=0, post-check=0'),
        ('eq', 'content-encoding', 'gzip',
        ('eq', 'content-length', '55'),
        ('eq', 'content-type', 'text/plain'),
        #('eq', 'content-length', None),
        ('eq', 'x-xss-protection', '0')
        ]

    # GAE does not allow setting content-encoding header and although it is set
    # when making the request with a browser, it is not set here when using
    # httplib.
    # TODO! Is there a way to trick GAE into thinking this request is
    # coming from a browser?
    if not test_utils.LOCAL:
      response_headers[3] = ('eq', 'content-encoding', None)
      response_headers[4] = ('eq', 'content-length', None)
      response_headers.append(('eq', 'transfer-encoding', 'chunked'))

    headers = update_browser_headers(
        [('User-Agent', 'testing :: not found')])

    print headers

    for method in METHODS:
      body = make_fake_body(method)
      if body:
        headers.update([('Content-Length', len(body))])

      response = test_utils.make_http_request(
          method=method,
          url=url,
          body=body,
          headers=headers)

      self.assertEqual(response.status, 404,
          'status for method %s is %d' % (method, response.status))

      if method == 'HEAD':
        response_headers[6] = ('eq', 'content-length', '0')
        # GAE Servers remove the x-xss-protection header when there is no content.
        expected_body = ''
      else:
        response_headers[6] = ('eq', 'content-length', '55')
        #response_headers[5] = ('eq', 'content-length', None)
        expected_body = 'Could not find url %s%s'% (test_utils.HOST, url)

      check_headers(self, response, response_headers, method)

      self.assertEqual(response.body, expected_body,
          'body %s for method %s' % (response.body, method))

  def test_robots(self):
    """Check for robots.txt response."""
    url = '/robots.txt'

    response_headers = [
        # TODO: Date header should be tested with a regex.
        ('len', 'date', 29),
        # TODO: A more robust check of the Expires header.
        ('len', 'expires', 29),
        ('eq', 'cache-control', 'public, max-age=1814400'),
        # The Content-* headers should not have values for a HEAD request, but
        # the GAE static file server that puts them there, so there's not
        # anything we can do about it.
        ('eq', 'content-encoding', None),
        ('eq', 'content-type', 'text/plain'),
        # GAE does not set the x-xss-protection header for text/plain.
        ('eq', 'x-xss-protection', None)
        ]

    # The GAE server does not send a content length header from static files if
    # the Content-Type is text/plain.
    if test_utils.LOCAL:
      response_headers.append(('eq', 'content-length', '23'))
    else:
      response_headers.append(('eq', 'content-length', None))

    headers = update_browser_headers(
        [('User-Agent', 'testing :: robots.txt')])

    for method in METHODS:
      body = make_fake_body(method)
      if body:
        headers.update([('Content-Length', len(body))])

      response = test_utils.make_http_request(
          method=method,
          url=url,
          body=body,
          headers=headers)

      self.assertEqual(response.status, 200,
          'status for method %s is %d' % (method, response.status))

      if method == 'HEAD':
        expected_body = ''
      else:
        expected_body = 'User-agent: *\nAllow: /\n'

      check_headers(self, response, response_headers, method)

      self.assertEqual(response.body, expected_body,
          'body %s for method %s' % (response.body, method))

  def test_sitemap(self):
    """Check for sitemap.xml response.
    """
    url = '/sitemap.xml'

    response_headers = [
        # TODO: Date header should be tested with a regex.
        ('len', 'date', 29),
        # TODO: A more robust check of the Expires header.
        ('len', 'expires', 29),
        ('eq', 'cache-control', 'public, max-age=86400'),
        # The Content-* headers should not have values for a HEAD request, but
        # the GAE static file server that puts them there, so there's not
        # anything we can do about it.
        ('eq', 'content-encoding', None),
        ('eq', 'content-type', 'application/xml'),
        ('eq', 'content-length', '1225'),
        # GAE does not set the x-xss-protection header for application/xml.
        ('eq', 'x-xss-protection', None)
        ]

    headers = update_browser_headers(
        [('User-Agent', 'testing :: site map')])

    for method in METHODS:

      body = make_fake_body(method)
      if body:
        headers.update([('Content-Length', len(body))])

      response = test_utils.make_http_request(
          method=method,
          url=url,
          body=body,
          headers=headers)

      self.assertEqual(response.status, 200,
          'status for method %s is %d' % (method, response.status))

      if method == 'HEAD':
        expected_body = 0
      else:
        expected_body = 1225

      check_headers(self, response, response_headers, method)

      # TODO: A more robust check of the site map contents.
      self.assertEqual(len(response.body), expected_body,
          'body %s for method %s' % (len(response.body), method))

  def test_goog_verify(self):
    """Check for google verification response.
    """
    url = '/googlef734612d306d87e6.html'

    response_headers = [
        # TODO: Date header should be tested with a regex.
        ('len', 'date', 29),
        # TODO: A more robust check of the Expires header.
        ('len', 'expires', 29),
        ('eq', 'cache-control', 'public, max-age=1814400'),
        # The Content-* headers should not have values for a HEAD request, but
        # the GAE static file server that puts them there, so there's not
        # anything we can do about it.
        ('eq', 'content-encoding', None),
        ('eq', 'content-type', 'text/html'),
        ('eq', 'x-xss-protection', None)
        ]

    # Why doesn't the GAE static file server set the Content-Length?
    if test_utils.LOCAL:
      response_headers.append(('eq', 'content-length', '53'))
    else:
      response_headers.append(('eq', 'content-length', None))

    headers = update_browser_headers([
      ('Accept-Encoding', 'deflate'),
      ('User-Agent', 'testing :: Google verification')])

    for method in METHODS:
      body = make_fake_body(method)
      if body:
        headers.update([('Content-Length', len(body))])

      response = test_utils.make_http_request(
          method=method,
          url=url,
          body=body,
          headers=headers)

      self.assertEqual(response.status, 200,
          'status for method %s is %d' % (method, response.status))

      if method == 'HEAD':
        expected_body = ''
      else:
        expected_body = 'google-site-verification: googlef734612d306d87e6.html'

      check_headers(self, response, response_headers, method)

      self.assertEqual(response.body, expected_body,
          'body %s for method %s' % (response.body, method))

