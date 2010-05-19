import re
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

HTTP_DATE_RX = re.compile('^[SMTWF]{1}[unoedhriat]{2}, [0-3]{1}[0-9]{1} [JFMASOND]{1}[anebrpyulgctov]{2} 20[0-9]{2} [012]{1}[0-9]{1}:[0-5]{1}[0-9]{1}:[0-5]{1}[0-9]{1} GMT$')

NO_CACHE_HEADER = 'no-cache, no-store, must-revalidate, pre-check=0, post-check=0'

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
    if type == 'regex':
      assert expected_value.match(value), \
          ('header %s: %s ; does not match regex %s' %
              (k, value, expected_value))
      continue
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

    content_length = test_utils.LOCAL and 238 or 200
    server = test_utils.LOCAL and 'Development/1.0' or 'Google Frontend'
    if test_utils.LOCAL:
      content_encoding = None
    else:
      content_encoding = 'gzip'

    body_rx = re.compile('.+404 Not Found.+')

    response_headers = [
        ('eq', 'server', server),
        ('regex', 'date', HTTP_DATE_RX),
        ('eq', 'expires', '-1'),
        ('eq', 'pragma', 'no-cache'),
        ('eq', 'cache-control', NO_CACHE_HEADER),
        ('eq', 'content-encoding', content_encoding),
        ('eq', 'content-length', content_length),
        ('eq', 'content-type', 'text/html; charset=utf-8'),
        ('eq', 'x-xss-protection', '0')
        ]

    headers = BROWSER_HEADERS

    for method in METHODS:
      body = make_fake_body(method)
      if body:
        headers.update([('Content-Length', len(body))])
      elif headers.get('Content-Length'):
        # A content-length header will confuse the server if there is no
        # content sent in the request.
        del headers['Content-Length']

      response = test_utils.make_http_request(
          method=method,
          url=url,
          body=body,
          headers=headers)

      self.assertEqual(response.status, 404,
          'status for method %s is %d' % (method, response.status))

      if method == 'HEAD':
        self.assertEqual(len(response.body), 0,
            'body len()=%d for method %s' % (len(response.body), method))
        response_headers[5] = ('eq', 'content-encoding', None)
        response_headers[6] = ('eq', 'content-length', '0')
      else:
        if test_utils.LOCAL:
          assert body_rx.search(response.body), \
              ('body \n%s\ndoes not match regex %s' % (response.body, body_rx.pattern))
        else:
          assert isinstance(response.body, str), \
              ('body \n%s\nis not an instance of str() but %r' %
                  (response.body, type(response.body)))
        response_headers[5] = ('eq', 'content-encoding', content_encoding)
        response_headers[6] = ('eq', 'content-length', str(content_length))

      check_headers(self, response, response_headers, method)

  def test_robots(self):
    """Check for robots.txt response."""
    url = '/robots.txt'

    response_headers = [
        ('len', 'etag', 8),
        ('eq', 'server', 'Google Frontend'),
        ('regex', 'date', HTTP_DATE_RX),
        ('regex', 'expires', HTTP_DATE_RX),
        ('eq', 'cache-control', 'public, max-age=1814400'),
        ('eq', 'content-encoding', 'gzip'),
        ('eq', 'content-length', '43'), # Set by GAE even with HEAD req
        ('eq', 'content-type', 'text/plain')
        ]

    if test_utils.LOCAL:
      response_headers[0] = ('eq', 'etag', None)
      response_headers[1] = ('eq', 'server', 'Development/1.0')
      response_headers[5] = ('eq', 'content-encoding', None)
      response_headers[6] = ('eq', 'content-length', '23')

    headers = BROWSER_HEADERS

    for method in METHODS:
      body = make_fake_body(method)
      if body:
        headers.update([('Content-Length', len(body))])
      elif headers.get('Content-Length'):
        del headers['Content-Length']

      response = test_utils.make_http_request(
          method=method,
          url=url,
          body=body,
          headers=headers)

      # Static GAE server does not send back 405 for unsupported request methods.
      self.assertEqual(response.status, 200,
          'status for method %s is %d' % (method, response.status))

      check_headers(self, response, response_headers, method)

      if method == 'HEAD':
        self.assertEqual(response.body, '',
            'body %s for method %s' % (response.body, method))

      assert isinstance(response.body, str), \
          'response body is %r for %s'% (type(response.body), method)

  def test_sitemap(self):
    """Check for sitemap.xml response.
    """
    url = '/sitemap.xml'

    response_headers = [
        ('len', 'etag', 8),
        ('eq', 'server', 'Google Frontend'),
        ('regex', 'date', HTTP_DATE_RX),
        ('regex', 'expires', HTTP_DATE_RX),
        ('eq', 'cache-control', 'public, max-age=86400'),
        # GAE static does not gzip application/xml
        ('eq', 'content-encoding', None),
        # Set by GAE static server even with HEAD req
        ('eq', 'content-length', '1225'),
        ('eq', 'content-type', 'application/xml')
        ]

    body_len = 1225

    if test_utils.LOCAL:
      body_len = 1225
      response_headers[0] = ('eq', 'etag', None)
      response_headers[1] = ('eq', 'server', 'Development/1.0')
      response_headers[5] = ('eq', 'content-encoding', None)
      response_headers[6] = ('eq', 'content-length', '1225')

    headers = BROWSER_HEADERS

    for method in METHODS:
      body = make_fake_body(method)
      if body:
        headers.update([('Content-Length', len(body))])
      elif headers.get('Content-Length'):
        del headers['Content-Length']

      response = test_utils.make_http_request(
          method=method,
          url=url,
          body=body,
          headers=headers)

      # Static GAE server does not send back 405 for unsupported request methods.
      self.assertEqual(response.status, 200,
          'status for method %s is %d' % (method, response.status))

      check_headers(self, response, response_headers, method)

      assert isinstance(response.body, str), \
          'response body is %r for %s'% (type(response.body), method)

      if method == 'HEAD':
        self.assertEqual(response.body, '',
            'body %s for method %s' % (response.body, method))
      else:
        self.assertEqual(len(response.body), body_len,
            'body %d for method %s' % (len(response.body), method))

  def test_goog_verify(self):
    """Check for google verification response.
    """
    url = '/googlef734612d306d87e6.html'

    response_headers = [
        ('len', 'etag', 8),
        ('eq', 'server', 'Google Frontend'),
        ('regex', 'date', HTTP_DATE_RX),
        ('regex', 'expires', HTTP_DATE_RX),
        ('eq', 'cache-control', 'public, max-age=1814400'),
        ('eq', 'content-encoding', 'gzip'),
        ('eq', 'content-length', '70'), # Set by GAE even with HEAD req
        ('eq', 'content-type', 'text/html')
        ]

    if test_utils.LOCAL:
      response_headers[0] = ('eq', 'etag', None)
      response_headers[1] = ('eq', 'server', 'Development/1.0')
      response_headers[5] = ('eq', 'content-encoding', None)
      response_headers[6] = ('eq', 'content-length', '53')

    headers = BROWSER_HEADERS

    for method in METHODS:
      body = make_fake_body(method)
      if body:
        headers.update([('Content-Length', len(body))])
      elif headers.get('Content-Length'):
        del headers['Content-Length']

      response = test_utils.make_http_request(
          method=method,
          url=url,
          body=body,
          headers=headers)

      # Static GAE server does not send back 405 for unsupported request methods.
      self.assertEqual(response.status, 200,
          'status for method %s is %d' % (method, response.status))

      check_headers(self, response, response_headers, method)

      assert isinstance(response.body, str), \
          'response body is %r for %s'% (type(response.body), method)

      if method == 'HEAD':
        self.assertEqual(response.body, '',
            'body %s for method %s' % (response.body, method))

