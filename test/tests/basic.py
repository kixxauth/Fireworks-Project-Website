import re
import unittest
import test_utils

class Defaults(unittest.TestCase):
  # TODO: Test favicon.ico

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
        ('regex', 'date', test_utils.HTTP_DATE_RX),
        ('eq', 'expires', '-1'),
        ('eq', 'pragma', 'no-cache'),
        ('eq', 'cache-control', test_utils.NO_CACHE_HEADER),
        ('eq', 'content-encoding', content_encoding),
        ('eq', 'content-length', content_length),
        ('eq', 'content-type', 'text/html; charset=utf-8'),
        ('eq', 'x-xss-protection', '0')
        ]

    headers = test_utils.update_browser_headers()

    for method in test_utils.METHODS:
      body = test_utils.make_fake_body(method)
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

      test_utils.check_headers(self, response, response_headers, method)

  def test_robots(self):
    """Check for robots.txt response."""
    url = '/robots.txt'

    response_headers = [
        ('len', 'etag', 8),
        ('eq', 'server', 'Google Frontend'),
        ('regex', 'date', test_utils.HTTP_DATE_RX),
        ('regex', 'expires', test_utils.HTTP_DATE_RX),
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

    headers = test_utils.update_browser_headers()

    for method in test_utils.METHODS:
      body = test_utils.make_fake_body(method)
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

      test_utils.check_headers(self, response, response_headers, method)

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
        ('regex', 'date', test_utils.HTTP_DATE_RX),
        ('regex', 'expires', test_utils.HTTP_DATE_RX),
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

    headers = test_utils.update_browser_headers()

    for method in test_utils.METHODS:
      body = test_utils.make_fake_body(method)
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

      test_utils.check_headers(self, response, response_headers, method)

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
        ('regex', 'date', test_utils.HTTP_DATE_RX),
        ('regex', 'expires', test_utils.HTTP_DATE_RX),
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

    headers = test_utils.update_browser_headers()

    for method in test_utils.METHODS:
      body = test_utils.make_fake_body(method)
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

      test_utils.check_headers(self, response, response_headers, method)

      assert isinstance(response.body, str), \
          'response body is %r for %s'% (type(response.body), method)

      if method == 'HEAD':
        self.assertEqual(response.body, '',
            'body %s for method %s' % (response.body, method))

