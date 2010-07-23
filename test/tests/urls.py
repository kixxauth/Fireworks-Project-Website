"""
  FWPWebsite test.tests.urls
  ~~~~~~~~~~~~~~~~~~~~~~~~~~
  Module containing the test classes referenced in `test/config.yaml`.

  :copyright: (c) 2010 by The Fireworks Project.
  :license: MIT, see LICENSE for more details.
"""

import re
import datetime
import random
import urllib
import hashlib
import hmac
import unittest
import test_utils

# Reassign the test decorator function to something nicer.
test_function = test_utils.test_function

# Create the request object we'll use for all the tests.
firefox36_config = test_utils.TestRequest()

# This is a set of request headers that mimic a web browser.
# Again, if you don't know what a header is you should read the HTTP spec.
# http://tools.ietf.org/html/rfc2616#section-14
#
# TODO: Test other browsers. (This is Firefox 3.6.3)
firefox36_config.headers = dict([
    ('Host', True),
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

# Finish setting up the test request configs.
firefox36_config.body = ''

# Set up the expected response tests.
firefox36_config.response_status = 200
firefox36_config.response_headers = []
# Setting response body to True will cause the test to simply
# assert that a response body exists.
firefox36_config.response_body = True

class RobotsTxt(unittest.TestCase):
  url = '/robots.txt'

  def configure(self):
    """Set up the request/response data.

    The test_utils.test_function decorator will cause this method
    to be called once for this test class, but NOT each time a test
    function is called.
    """
    # Make a copy of the configs.
    self.firefox36 = test_utils.TestRequest(firefox36_config)

    # Set up tests for a local dev_appserver response.
    if test_utils.LOCAL:
      self.firefox36.response_headers = [
            ('etag', 'eq', None),
            ('server', 'eq', 'Development/1.0'),
            ('date', 'regex', test_utils.HTTP_DATE_RX),
            ('expires', 'regex', test_utils.HTTP_DATE_RX),
            ('cache-control', 'eq', 'public, max-age=1814400'),
            ('content-encoding', 'eq', None),
            ('content-length', 'eq', '23'),
            ('content-type', 'eq', 'text/plain')
          ]
      # Test the response body against a regex.
      self.firefox36.response_body = re.compile('User-agent: \*\\nAllow: \/\\n')

    # Set up tests for a production server response.
    else:
      self.firefox36.response_headers = [
            ('etag', 'len', 8),
            ('server', 'eq', 'Google Frontend'),
            ('date', 'regex', test_utils.HTTP_DATE_RX),
            ('expires', 'regex', test_utils.HTTP_DATE_RX),
            ('cache-control', 'eq', 'public, max-age=1814400'),
            ('content-encoding', 'eq', 'gzip'),
            ('content-length', 'eq', '43'),
            ('content-type', 'eq', 'text/plain')
          ]
      # Test the length of the response body.
      self.firefox36.response_body = 43

  @test_function
  def get(self):
    """GET request for robots.txt
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

  @test_function
  def put(self):
    """PUT request for robots.txt
    """
    # Make a copy of the test configs.
    ff36 = test_utils.TestRequest(self.firefox36)
    # Set aditional request configs.
    ff36.body = 'User-agent: *\nAllow: /\n'
    ff36.headers['Content-Length'] = str(len(ff36.body))
    ff36.headers['Content-Type'] = 'text/plain'
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def post(self):
    """POST request for robots.txt
    """
    ff36 = test_utils.TestRequest(self.firefox36)
    ff36.body = 's=foo&num=44'
    ff36.headers['Content-Length'] = str(len(ff36.body))
    ff36.headers['Content-Type'] = 'application/x-www-form-urlencoded'
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def delete(self):
    """DELETE request for robots.txt
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

  @test_function
  def head(self):
    """HEAD request for robots.txt
    """
    ff36 = test_utils.TestRequest(self.firefox36)
    # GAE dev and production static file servers both set the Content-Length
    # header even when there is no content body returned.
    if test_utils.LOCAL:
      ff36.response_headers[6] = ('content-length', 'eq', '23')
    else:
      ff36.response_headers[6] = ('content-length', 'eq', '43')
    ff36.response_body = None
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def options(self):
    """OPTIONS request for robots.txt
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

  @test_function
  def trace(self):
    """TRACE request for robots.txt
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

class Sitemap(unittest.TestCase):
  url = '/sitemap.xml'

  def configure(self):
    """Set up the request/response data.

    The test_utils.test_function decorator will cause this method
    to be called once for this test class, but NOT each time a test
    function is called.
    """
    self.firefox36 = test_utils.TestRequest(firefox36_config)
    self.firefox36.response_body = 1225

    if test_utils.LOCAL:
      self.firefox36.response_headers = [
            ('etag', 'eq', None),
            ('server', 'eq', 'Development/1.0'),
            ('date', 'regex', test_utils.HTTP_DATE_RX),
            ('expires', 'regex', test_utils.HTTP_DATE_RX),
            ('cache-control', 'eq', 'public, max-age=86400'),
            ('content-encoding', 'eq', None),
            ('content-length', 'eq', '1225'),
            ('content-type', 'eq', 'application/xml')
          ]

    else:
      self.firefox36.response_headers = [
            ('etag', 'len', 8),
            ('server', 'eq', 'Google Frontend'),
            ('date', 'regex', test_utils.HTTP_DATE_RX),
            ('expires', 'regex', test_utils.HTTP_DATE_RX),
            ('cache-control', 'eq', 'public, max-age=86400'),
            # GAE does static file servers do not gzip xml.
            ('content-encoding', 'eq', None),
            ('content-length', 'eq', '1225'),
            ('content-type', 'eq', 'application/xml')
          ]

  @test_function
  def get(self):
    """GET request for sitemap.xml
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

  @test_function
  def put(self):
    """PUT request for sitemap.xml
    """
    ff36 = test_utils.TestRequest(self.firefox36)
    ff36.body = 'User-agent: *\nAllow: /\n'
    ff36.headers['Content-Length'] = str(len(ff36.body))
    ff36.headers['Content-Type'] = 'text/plain'
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def post(self):
    """POST request for sitemap.xml
    """
    ff36 = test_utils.TestRequest(self.firefox36)
    ff36.body = 's=foo&num=44'
    ff36.headers['Content-Length'] = str(len(ff36.body))
    ff36.headers['Content-Type'] = 'application/x-www-form-urlencoded'
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def delete(self):
    """DELETE request for sitemap.xml
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

  @test_function
  def head(self):
    """HEAD request for sitemap.xml
    """
    ff36 = test_utils.TestRequest(self.firefox36)
    # GAE dev and production static file servers both set the Content-Length
    # header even when there is no content body returned.
    ff36.response_headers[6] = ('content-length', 'eq', '1225')
    ff36.response_body = None
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def options(self):
    """OPTIONS request for sitemap.xml
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

  @test_function
  def trace(self):
    """TRACE request for sitemap.xml
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

class GoogleVerify(unittest.TestCase):
  url = '/googlef734612d306d87e6.html'

  def configure(self):
    """Set up the request/response data.

    The test_utils.test_function decorator will cause this method
    to be called once for this test class, but NOT each time a test
    function is called.
    """
    self.firefox36 = test_utils.TestRequest(firefox36_config)

    if test_utils.LOCAL:
      self.firefox36.response_headers = [
            ('etag', 'eq', None),
            ('server', 'eq', 'Development/1.0'),
            ('date', 'regex', test_utils.HTTP_DATE_RX),
            ('expires', 'regex', test_utils.HTTP_DATE_RX),
            ('cache-control', 'eq', 'public, max-age=1814400'),
            ('content-encoding', 'eq', None),
            ('content-length', 'eq', '53'),
            ('content-type', 'eq', 'text/html')
          ]
      self.firefox36.response_body = 53

    else:
      self.firefox36.response_headers = [
            ('etag', 'len', 8),
            ('server', 'eq', 'Google Frontend'),
            ('date', 'regex', test_utils.HTTP_DATE_RX),
            ('expires', 'regex', test_utils.HTTP_DATE_RX),
            ('cache-control', 'eq', 'public, max-age=1814400'),
            ('content-encoding', 'eq', 'gzip'),
            ('content-length', 'eq', '70'),
            ('content-type', 'eq', 'text/html')
          ]
      self.firefox36.response_body = 70

  @test_function
  def get(self):
    """GET request for Google Verify
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

  @test_function
  def put(self):
    """PUT request for Google Verify
    """
    ff36 = test_utils.TestRequest(self.firefox36)
    ff36.body = 'User-agent: *\nAllow: /\n'
    ff36.headers['Content-Length'] = str(len(ff36.body))
    ff36.headers['Content-Type'] = 'text/plain'
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def post(self):
    """POST request for Google Verify
    """
    ff36 = test_utils.TestRequest(self.firefox36)
    ff36.body = 's=foo&num=44'
    ff36.headers['Content-Length'] = str(len(ff36.body))
    ff36.headers['Content-Type'] = 'application/x-www-form-urlencoded'
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def delete(self):
    """DELETE request for Google Verify
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

  @test_function
  def head(self):
    """HEAD request for Google Verify
    """
    ff36 = test_utils.TestRequest(self.firefox36)
    # GAE dev and production static file servers both set the Content-Length
    # header even when there is no content body returned.
    if test_utils.LOCAL:
      ff36.response_headers[6] = ('content-length', 'eq', '53')
    else:
      ff36.response_headers[6] = ('content-length', 'eq', '70')
    ff36.response_body = None
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def options(self):
    """OPTIONS request for Google Verify
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

  @test_function
  def trace(self):
    """TRACE request for Google Verify
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

class NotFound(unittest.TestCase):
  url = '/lost_city_of_atlantis'

  def configure(self):
    """Set up the request/response data.

    The test_utils.test_function decorator will cause this method
    to be called once for this test class, but NOT each time a test
    function is called.
    """
    self.firefox36 = test_utils.TestRequest(firefox36_config)
    self.firefox36.response_status = 404

    if test_utils.LOCAL:
      self.firefox36.response_headers = [
            ('etag', 'eq', None),
            ('server', 'eq', 'Development/1.0'),
            ('date', 'regex', test_utils.HTTP_DATE_RX),
            ('expires', 'eq', '-1'),
            ('pragma', 'eq', 'no-cache'),
            ('cache-control', 'eq', test_utils.NO_CACHE_HEADER),
            ('content-encoding', 'eq', None),
            ('content-length', 'eq', '238'),
            ('content-type', 'eq', 'text/html; charset=utf-8'),
            ('x-xss-protection', 'eq', '0')
          ]
      self.firefox36.response_body = 238

    else:
      self.firefox36.response_headers = [
            ('etag', 'eq', None),
            ('server', 'eq', 'Google Frontend'),
            ('date', 'regex', test_utils.HTTP_DATE_RX),
            ('expires', 'eq', '-1'),
            ('pragma', 'eq', 'no-cache'),
            ('cache-control', 'eq', test_utils.NO_CACHE_HEADER),
            ('content-encoding', 'eq', 'gzip'),
            ('content-length', 'eq', '200'),
            ('content-type', 'eq', 'text/html; charset=utf-8'),
            ('x-xss-protection', 'eq', '0')
          ]
      self.firefox36.response_body = 200

  @test_function
  def get(self):
    """GET request for Not Found
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

  @test_function
  def put(self):
    """PUT request for Not Found
    """
    ff36 = test_utils.TestRequest(self.firefox36)
    ff36.body = 'User-agent: *\nAllow: /\n'
    ff36.headers['Content-Length'] = str(len(ff36.body))
    ff36.headers['Content-Type'] = 'text/plain'
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def post(self):
    """POST request for Not Found
    """
    ff36 = test_utils.TestRequest(self.firefox36)
    ff36.body = 's=foo&num=44'
    ff36.headers['Content-Length'] = str(len(ff36.body))
    ff36.headers['Content-Type'] = 'application/x-www-form-urlencoded'
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def delete(self):
    """DELETE request for Not Found
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

  @test_function
  def head(self):
    """HEAD request for Not Found
    """
    ff36 = test_utils.TestRequest(self.firefox36)
    ff36.response_headers[6] = ('content-encoding', 'eq', None)
    ff36.response_headers[7] = ('content-length', 'eq', '0')
    ff36.response_body = None
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def options(self):
    """OPTIONS request for Not Found
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

  @test_function
  def trace(self):
    """TRACE request for Not Found
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

class Root(unittest.TestCase):
  url = '/'

  def configure(self):
    """Set up the request/response data.

    The test_utils.test_function decorator will cause this method
    to be called once for this test class, but NOT each time a test
    function is called.
    """
    self.firefox36 = test_utils.TestRequest(firefox36_config)
    self.firefox36.response_status = 200
    self.firefox36.response_body = True

    if test_utils.LOCAL:
      self.firefox36.response_headers = [
            ('etag', 'regex', re.compile('"[0-9a-f]{32}"')),
            ('server', 'eq', 'Development/1.0'),
            ('date', 'regex', test_utils.HTTP_DATE_RX),
            ('expires', 'regex', test_utils.HTTP_DATE_RX),
            ('pragma', 'eq', None),
            # Expire in 4 days.
            ('cache-control', 'eq', 'public, max-age=345600'),
            ('content-encoding', 'eq', None),
            ('content-length', 'regex', re.compile('[0-9]+')),
            ('content-type', 'eq', 'text/html; charset=utf-8'),
            ('x-xss-protection', 'eq', '0')
          ]

    else:
      self.firefox36.response_headers = [
            ('etag', 'regex', re.compile('"[0-9a-f]{32}"')),
            ('server', 'eq', 'Google Frontend'),
            ('date', 'regex', test_utils.HTTP_DATE_RX),
            ('expires', 'regex', test_utils.HTTP_DATE_RX),
            ('pragma', 'eq', None),
            # Expire in 4 days.
            ('cache-control', 'eq', 'public, max-age=345600'),
            ('content-encoding', 'eq', 'gzip'),
            ('content-length', 'regex', re.compile('[0-9]+')),
            ('content-type', 'eq', 'text/html; charset=utf-8'),
            ('x-xss-protection', 'eq', '0')
          ]

    # Make a special request for the not allowed method tests.
    self.firefox36_not_allowed = test_utils.TestRequest(self.firefox36)
    self.firefox36_not_allowed.response_status = 405

    # The error page is served in simple text/html.
    self.firefox36_not_allowed.response_body = True
    self.firefox36_not_allowed.response_headers[8] = ('content-type', 'eq', 'text/html')
    self.firefox36_not_allowed.response_headers[9] = ('x-xss-protection', 'eq', None)
    self.firefox36_not_allowed.response_headers.append(
        ('allow', 'eq', 'GET, HEAD'))
    self.firefox36_not_allowed.response_headers[0] = ('etag', 'eq', None)

    if test_utils.LOCAL:
      # The dev_appserver autimatically sets the Expires and Cache-Control
      # headers -- annoying.
      self.firefox36_not_allowed.response_headers[3] = (
          'expires', 'eq', 'Fri, 01 Jan 1990 00:00:00 GMT')
      self.firefox36_not_allowed.response_headers[5] = (
          'cache-control', 'eq', 'no-cache')
    else:
      self.firefox36_not_allowed.response_headers[3] = (
          'expires', 'eq', None)
      # And the production server automatically sets the Cache-Control header,
      # but I'm assuming this is because we don't set it in our 405 handler.
      # See issue #28
      self.firefox36_not_allowed.response_headers[5] = (
          'cache-control', 'eq', 'private, x-gzip-ok=""')

  @test_function
  def get(self):
    """GET request for /
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

  @test_function
  def put(self):
    """PUT request for /
    """
    ff36 = test_utils.TestRequest(self.firefox36_not_allowed)
    ff36.body = '<html>Some HTML</html>'
    ff36.headers['Content-Length'] = str(len(ff36.body))
    ff36.headers['Content-Type'] = 'text/html'
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def post(self):
    """POST request for /
    """
    ff36 = test_utils.TestRequest(self.firefox36_not_allowed)
    ff36.body = 's=foo&num=44'
    ff36.headers['Content-Length'] = str(len(ff36.body))
    ff36.headers['Content-Type'] = 'application/x-www-form-urlencoded'
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def delete(self):
    """DELETE request for /
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36_not_allowed)
    return configs.items()

  @test_function
  def head(self):
    """HEAD request for /
    """
    ff36 = test_utils.TestRequest(self.firefox36)
    ff36.response_headers[6] = ('content-encoding', 'eq', None)
    ff36.response_headers[7] = ('content-length', 'eq', '0')
    ff36.response_body = None
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def options(self):
    """OPTIONS request for /
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36_not_allowed)
    return configs.items()

  @test_function
  def trace(self):
    """TRACE request for /
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36_not_allowed)
    return configs.items()

class Join(unittest.TestCase):
  url = '/join'

  def configure(self):
    """Set up the request/response data.

    The test_utils.test_function decorator will cause this method
    to be called once for this test class, but NOT each time a test
    function is called.
    """
    # Make a copy of the test configs.
    self.firefox36 = test_utils.TestRequest(firefox36_config)
    self.firefox36.response_status = 200
    # Setting the response_body config to True will cause the test to
    # simply check to make sure the HTTP response body is there.
    self.firefox36.response_body = True

    if test_utils.LOCAL:
      self.firefox36.response_headers = [
            ('etag', 'regex', re.compile('"[0-9a-f]{32}"')),
            ('server', 'eq', 'Development/1.0'),
            ('date', 'regex', test_utils.HTTP_DATE_RX),
            ('expires', 'regex', test_utils.HTTP_DATE_RX),
            ('pragma', 'eq', None),
            # Expire in 4 days.
            ('cache-control', 'eq', 'public, max-age=345600'),
            ('content-encoding', 'eq', None),
            ('content-length', 'regex', re.compile('[0-9]+')),
            ('content-type', 'eq', 'text/html; charset=utf-8'),
            ('x-xss-protection', 'eq', '0')
          ]

    else:
      self.firefox36.response_headers = [
            ('etag', 'regex', re.compile('"[0-9a-f]{32}"')),
            ('server', 'eq', 'Google Frontend'),
            ('date', 'regex', test_utils.HTTP_DATE_RX),
            ('expires', 'regex', test_utils.HTTP_DATE_RX),
            ('pragma', 'eq', None),
            # Expire in 4 days.
            ('cache-control', 'eq', 'public, max-age=345600'),
            ('content-encoding', 'eq', 'gzip'),
            ('content-length', 'regex', re.compile('[0-9]+')),
            ('content-type', 'eq', 'text/html; charset=utf-8'),
            ('x-xss-protection', 'eq', '0')
          ]

    # Make a special request for the not allowed method tests.
    self.firefox36_not_allowed = test_utils.TestRequest(self.firefox36)
    self.firefox36_not_allowed.response_status = 405

    # The error page is served in simple text/html.
    self.firefox36_not_allowed.response_body = True
    self.firefox36_not_allowed.response_headers[8] = ('content-type', 'eq', 'text/html')
    self.firefox36_not_allowed.response_headers[9] = ('x-xss-protection', 'eq', None)
    self.firefox36_not_allowed.response_headers.append(
        ('allow', 'eq', 'GET, HEAD'))
    self.firefox36_not_allowed.response_headers[0] = ('etag', 'eq', None)

    if test_utils.LOCAL:
      # The dev_appserver autimatically sets the Expires and Cache-Control
      # headers -- annoying.
      self.firefox36_not_allowed.response_headers[3] = (
          'expires', 'eq', 'Fri, 01 Jan 1990 00:00:00 GMT')
      self.firefox36_not_allowed.response_headers[5] = (
          'cache-control', 'eq', 'no-cache')
    else:
      self.firefox36_not_allowed.response_headers[3] = (
          'expires', 'eq', None)
      # And the production server automatically sets the Cache-Control header,
      # but I'm assuming this is because we don't set it in our 405 handler.
      # See issue #28
      self.firefox36_not_allowed.response_headers[5] = (
          'cache-control', 'eq', 'private, x-gzip-ok=""')

  @test_function
  def get(self):
    """GET request for /join
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

  @test_function
  def put(self):
    """PUT request for /join
    """
    ff36 = test_utils.TestRequest(self.firefox36_not_allowed)
    ff36.body = '<html>Some HTML</html>'
    ff36.headers['Content-Length'] = str(len(ff36.body))
    ff36.headers['Content-Type'] = 'text/html'
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def post(self):
    """POST request for /join
    """
    ff36 = test_utils.TestRequest(self.firefox36_not_allowed)
    ff36.body = 's=foo&num=44'
    ff36.headers['Content-Length'] = str(len(ff36.body))
    ff36.headers['Content-Type'] = 'application/x-www-form-urlencoded'
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def delete(self):
    """DELETE request for /join
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36_not_allowed)
    return configs.items()

  @test_function
  def head(self):
    """HEAD request for /join
    """
    ff36 = test_utils.TestRequest(self.firefox36)
    ff36.response_headers[6] = ('content-encoding', 'eq', None)
    ff36.response_headers[7] = ('content-length', 'eq', '0')
    ff36.response_body = None
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def options(self):
    """OPTIONS request for /join
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36_not_allowed)
    return configs.items()

  @test_function
  def trace(self):
    """TRACE request for /join
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36_not_allowed)
    return configs.items()

class Projects(unittest.TestCase):
  url = '/projects/'

  def configure(self):
    """Set up the request/response data.

    The test_utils.test_function decorator will cause this method
    to be called once for this test class, but NOT each time a test
    function is called.
    """
    self.firefox36 = test_utils.TestRequest(firefox36_config)
    self.firefox36.response_status = 200
    self.firefox36.response_body = True

    if test_utils.LOCAL:
      self.firefox36.response_headers = [
            ('etag', 'regex', re.compile('"[0-9a-f]{32}"')),
            ('server', 'eq', 'Development/1.0'),
            ('date', 'regex', test_utils.HTTP_DATE_RX),
            ('expires', 'regex', test_utils.HTTP_DATE_RX),
            ('pragma', 'eq', None),
            # Expire in 4 days.
            ('cache-control', 'eq', 'public, max-age=345600'),
            ('content-encoding', 'eq', None),
            ('content-length', 'regex', re.compile('[0-9]+')),
            ('content-type', 'eq', 'text/html; charset=utf-8'),
            ('x-xss-protection', 'eq', '0')
          ]

    else:
      self.firefox36.response_headers = [
            ('etag', 'regex', re.compile('"[0-9a-f]{32}"')),
            ('server', 'eq', 'Google Frontend'),
            ('date', 'regex', test_utils.HTTP_DATE_RX),
            ('expires', 'regex', test_utils.HTTP_DATE_RX),
            ('pragma', 'eq', None),
            # Expire in 4 days.
            ('cache-control', 'eq', 'public, max-age=345600'),
            ('content-encoding', 'eq', 'gzip'),
            ('content-length', 'regex', re.compile('[0-9]+')),
            ('content-type', 'eq', 'text/html; charset=utf-8'),
            ('x-xss-protection', 'eq', '0')
          ]

    # Make a special request for the not allowed method tests.
    self.firefox36_not_allowed = test_utils.TestRequest(self.firefox36)
    self.firefox36_not_allowed.response_status = 405

    # The error page is served in simple text/html.
    self.firefox36_not_allowed.response_body = True
    self.firefox36_not_allowed.response_headers[8] = ('content-type', 'eq', 'text/html')
    self.firefox36_not_allowed.response_headers[9] = ('x-xss-protection', 'eq', None)
    self.firefox36_not_allowed.response_headers.append(
        ('allow', 'eq', 'GET, HEAD'))
    self.firefox36_not_allowed.response_headers[0] = ('etag', 'eq', None)

    if test_utils.LOCAL:
      # The dev_appserver autimatically sets the Expires and Cache-Control
      # headers -- annoying.
      self.firefox36_not_allowed.response_headers[3] = (
          'expires', 'eq', 'Fri, 01 Jan 1990 00:00:00 GMT')
      self.firefox36_not_allowed.response_headers[5] = (
          'cache-control', 'eq', 'no-cache')
    else:
      self.firefox36_not_allowed.response_headers[3] = (
          'expires', 'eq', None)
      # And the production server automatically sets the Cache-Control header,
      # but I'm assuming this is because we don't set it in our 405 handler.
      # See issue #28
      self.firefox36_not_allowed.response_headers[5] = (
          'cache-control', 'eq', 'private, x-gzip-ok=""')

  @test_function
  def get(self):
    """GET request for /projects/
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

  @test_function
  def put(self):
    """PUT request for /projects/
    """
    ff36 = test_utils.TestRequest(self.firefox36_not_allowed)
    ff36.body = '<html>Some HTML</html>'
    ff36.headers['Content-Length'] = str(len(ff36.body))
    ff36.headers['Content-Type'] = 'text/html'
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def post(self):
    """POST request for /projects/
    """
    ff36 = test_utils.TestRequest(self.firefox36_not_allowed)
    ff36.body = 's=foo&num=44'
    ff36.headers['Content-Length'] = str(len(ff36.body))
    ff36.headers['Content-Type'] = 'application/x-www-form-urlencoded'
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def delete(self):
    """DELETE request for /projects/
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36_not_allowed)
    return configs.items()

  @test_function
  def head(self):
    """HEAD request for /projects/
    """
    ff36 = test_utils.TestRequest(self.firefox36)
    ff36.response_headers[6] = ('content-encoding', 'eq', None)
    ff36.response_headers[7] = ('content-length', 'eq', '0')
    ff36.response_body = None
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def options(self):
    """OPTIONS request for /projects/
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36_not_allowed)
    return configs.items()

  @test_function
  def trace(self):
    """TRACE request for /projects/
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36_not_allowed)
    return configs.items()

class DatastoreMembers(unittest.TestCase):
  url = '/datastore/members/'

  def configure(self):
    """Set up the request/response data.

    The test_utils.test_function decorator will cause this method
    to be called once for this test class, but NOT each time a test
    function is called.
    """
    # Make a copy of the configs.
    self.firefox36 = test_utils.TestRequest(firefox36_config)
    self.firefox36.response_status = 200
    self.firefox36.response_body = True

    if test_utils.LOCAL:
      self.firefox36.response_headers = [
            ('etag', 'regex', re.compile('"[0-9a-f]{32}"')),
            ('server', 'eq', 'Development/1.0'),
            ('date', 'regex', test_utils.HTTP_DATE_RX),
            ('expires', 'eq', '-1'),
            ('pragma', 'eq', 'no-cache'),
            ('cache-control', 'eq', test_utils.NO_CACHE_HEADER),
            ('content-encoding', 'eq', None),
            ('content-length', 'regex', re.compile('[0-9]+')),
            ('content-type', 'eq', 'text/html; charset=utf-8'),
            ('x-xss-protection', 'eq', '0')
          ]

    else:
      self.firefox36.response_headers = [
            ('etag', 'regex', re.compile('"[0-9a-f]{32}"')),
            ('server', 'eq', 'Google Frontend'),
            ('date', 'regex', test_utils.HTTP_DATE_RX),
            ('expires', 'eq', '-1'),
            ('pragma', 'eq', 'no-cache'),
            ('cache-control', 'eq', test_utils.NO_CACHE_HEADER),
            ('content-encoding', 'eq', 'gzip'),
            ('content-length', 'regex', re.compile('[0-9]+')),
            ('content-type', 'eq', 'text/html; charset=utf-8'),
            ('x-xss-protection', 'eq', '0')
          ]

    # Make a special request for the not allowed method tests.
    self.firefox36_not_allowed = test_utils.TestRequest(self.firefox36)
    self.firefox36_not_allowed.response_status = 405

    # The error page is served in simple text/html.
    self.firefox36_not_allowed.response_body = True
    self.firefox36_not_allowed.response_headers[4] = ('pragma', 'eq', None)
    self.firefox36_not_allowed.response_headers[8] = ('content-type', 'eq', 'text/html')
    self.firefox36_not_allowed.response_headers[9] = ('x-xss-protection', 'eq', None)
    self.firefox36_not_allowed.response_headers.append(
        ('allow', 'eq', 'GET, POST, HEAD'))
    self.firefox36_not_allowed.response_headers[0] = ('etag', 'eq', None)

    if test_utils.LOCAL:
      # The dev_appserver autimatically sets the Expires and Cache-Control
      # headers -- annoying.
      self.firefox36_not_allowed.response_headers[3] = (
          'expires', 'eq', 'Fri, 01 Jan 1990 00:00:00 GMT')
      self.firefox36_not_allowed.response_headers[5] = (
          'cache-control', 'eq', 'no-cache')
    else:
      self.firefox36_not_allowed.response_headers[3] = (
          'expires', 'eq', None)
      # And the production server automatically sets the Cache-Control header,
      # but I'm assuming this is because we don't set it in our 405 handler.
      # See issue #28
      self.firefox36_not_allowed.response_headers[5] = (
          'cache-control', 'eq', 'private, x-gzip-ok=""')

  @test_function
  def get(self):
    """GET request for /datastore/members/
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

  @test_function
  def put(self):
    """PUT request for /datastore/members/
    """
    ff36 = test_utils.TestRequest(self.firefox36_not_allowed)
    ff36.body = '<html>Some HTML</html>'
    ff36.headers['Content-Length'] = str(len(ff36.body))
    ff36.headers['Content-Type'] = 'text/html'
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def post(self):
    """POST request for /datastore/members/

    #### TODO
    So far, this is only testing for a response. For complete testing we need
    to finish the functionality of the /datastore/ service and test the data
    integrity issues - read, write, delete, and permissions.

    Complete /datastore/ testing should be put into a dedicated module.
    """
    # Create a random email address, since that is how we distinguish unique
    # members.
    def random_email():
      return hmac.new(
          str(datetime.datetime.utcnow()).encode('ascii'),
          str(random.randint(0, 9999)).encode('ascii'),
          hashlib.sha1).hexdigest()

    # Make a copy of the generic test configs for standard HTML.
    ff36 = test_utils.TestRequest(self.firefox36)
    ff36.headers['Content-Type'] = 'application/x-www-form-urlencoded'

    # Make a copy of the generic test configs for AJAX.
    ff36_ajax = test_utils.TestRequest(ff36)
    ff36_ajax.headers['Accept'] = 'application/json'
    ff36_ajax.headers['X-Requested-With'] = 'XMLHttpRequest'
    ff36_ajax.response_headers[8] = ('content-type', 'eq', 'application/json')

    # Create the new member entity.
    ff36.body = urllib.urlencode({
        'name': 'Delete Me',
        'email': '%s@example.com'% random_email()
      })
    ff36.headers['Content-Length'] = str(len(ff36.body))
    ff36.response_status = 201

    # Repeat for AJAX
    ff36_ajax.body = urllib.urlencode({
        'name': 'Delete Me',
        'email': '%s@example.com'% random_email()
      })
    ff36_ajax.headers['Content-Length'] = str(len(ff36_ajax.body))
    ff36_ajax.response_status = 201

    # Make another copy of the test configs to test a form submission with no
    # 'name' data field.
    ff36_noname = test_utils.TestRequest(ff36)
    ff36_noname.body = urllib.urlencode({
        'name': '',
        'email': '%s@example.com'% random_email()
      })
    ff36_noname.headers['Content-Length'] = str(len(ff36_noname.body))
    ff36_noname.response_status = 409

    # Repeat for AJAX
    ff36_noname_ajax = test_utils.TestRequest(ff36_ajax)
    ff36_noname_ajax.body = urllib.urlencode({
        'name': '',
        'email': '%s@example.com'% random_email()
      })
    ff36_noname_ajax.headers['Content-Length'] = \
        str(len(ff36_noname_ajax.body))
    ff36_noname_ajax.response_status = 409

    # Make one more copy of the test configs to test a form submission that is
    # missing the 'email' data field.
    ff36_noemail = test_utils.TestRequest(ff36)
    ff36_noemail.body = urllib.urlencode({
        'name': 'Delete Me'
      })
    ff36_noemail.headers['Content-Length'] = str(len(ff36_noemail.body))
    ff36_noemail.response_status = 409

    # Repeat for AJAX
    ff36_noemail_ajax = test_utils.TestRequest(ff36_ajax)
    ff36_noemail_ajax.body = urllib.urlencode({
        'name': 'Delete Me'
      })
    ff36_noemail_ajax.headers['Content-Length'] = \
        str(len(ff36_noemail_ajax.body))
    ff36_noemail_ajax.response_status = 409

    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    configs.update('firefox36_ajax', ff36_ajax)
    configs.update('firefox36_noname', ff36_noname)
    configs.update('firefox36_noname_ajax', ff36_noname_ajax)
    configs.update('firefox36_noemail', ff36_noemail)
    configs.update('firefox36_noemail_ajax', ff36_noemail_ajax)
    return configs.items()

  @test_function
  def delete(self):
    """DELETE request for /datastore/members/
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36_not_allowed)
    return configs.items()

  @test_function
  def head(self):
    """HEAD request for /datastore/members/
    """
    ff36 = test_utils.TestRequest(self.firefox36)
    ff36.response_headers[6] = ('content-encoding', 'eq', None)
    ff36.response_headers[7] = ('content-length', 'eq', '0')
    ff36.response_body = None
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def options(self):
    """OPTIONS request for /datastore/members/
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36_not_allowed)
    return configs.items()

  @test_function
  def trace(self):
    """TRACE request for /datastore/members/
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36_not_allowed)
    return configs.items()

class DatastoreMembersInvalid(unittest.TestCase):
  """The /datastore/members/ URL must have a '/' on the end of it."""

  url = '/datastore/members'

  def configure(self):
    """Set up the request/response data.

    The test_utils.test_function decorator will cause this method
    to be called once for this test class, but NOT each time a test
    function is called.
    """
    self.firefox36 = test_utils.TestRequest(firefox36_config)
    self.firefox36.response_status = 301
    self.firefox36.response_body = True

    if test_utils.LOCAL:
      self.firefox36.response_headers = [
            ('etag', 'eq', None),
            ('server', 'eq', 'Development/1.0'),
            ('date', 'regex', test_utils.HTTP_DATE_RX),
            ('expires', 'regex', test_utils.HTTP_DATE_RX),
            ('pragma', 'eq', None),
            # Expire in 4 weeks.
            ('cache-control', 'eq', 'public, max-age=2419200'),
            ('content-encoding', 'eq', None),
            ('content-length', 'eq', '287'),
            ('content-type', 'eq', 'text/html; charset=utf-8'),
            ('x-xss-protection', 'eq', '0')
          ]

    else:
      self.firefox36.response_headers = [
            ('etag', 'eq', None),
            ('server', 'eq', 'Google Frontend'),
            ('date', 'regex', test_utils.HTTP_DATE_RX),
            ('expires', 'regex', test_utils.HTTP_DATE_RX),
            ('pragma', 'eq', None),
            # Expire in 4 weeks.
            ('cache-control', 'eq', 'public, max-age=2419200'),
            ('content-encoding', 'eq', 'gzip'),
            ('content-length', 'eq', '229'),
            ('content-type', 'eq', 'text/html; charset=utf-8'),
            ('x-xss-protection', 'eq', '0')
          ]

  @test_function
  def get(self):
    """GET request for /datastore/members Invalid
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

  @test_function
  def put(self):
    """PUT request for /datastore/members Invalid
    """
    ff36 = test_utils.TestRequest(self.firefox36)
    ff36.body = 'User-agent: *\nAllow: /\n'
    ff36.headers['Content-Length'] = str(len(ff36.body))
    ff36.headers['Content-Type'] = 'text/plain'
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def post(self):
    """POST request for /datastore/members Invalid
    """
    ff36 = test_utils.TestRequest(self.firefox36)
    ff36.body = 's=foo&num=44'
    ff36.headers['Content-Length'] = str(len(ff36.body))
    ff36.headers['Content-Type'] = 'application/x-www-form-urlencoded'
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def delete(self):
    """DELETE request for /datastore/members Invalid
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

  @test_function
  def head(self):
    """HEAD request for /datastore/members Invalid
    """
    ff36 = test_utils.TestRequest(self.firefox36)
    ff36.response_headers[6] = ('content-encoding', 'eq', None)
    ff36.response_headers[7] = ('content-length', 'eq', '0')
    ff36.response_body = None
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def options(self):
    """OPTIONS request for /datastore/members Invalid
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

  @test_function
  def trace(self):
    """TRACE request for /datastore/members Invalid
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

class DatastoreSubscribers(unittest.TestCase):
  url = '/datastore/subscribers/'

  def configure(self):
    """Set up the request/response data.

    The test_utils.test_function decorator will cause this method
    to be called once for this test class, but NOT each time a test
    function is called.
    """
    # Make a copy of the configs.
    self.firefox36 = test_utils.TestRequest(firefox36_config)
    self.firefox36.response_status = 200
    self.firefox36.response_body = True

    if test_utils.LOCAL:
      self.firefox36.response_headers = [
            ('etag', 'regex', re.compile('"[0-9a-f]{32}"')),
            ('server', 'eq', 'Development/1.0'),
            ('date', 'regex', test_utils.HTTP_DATE_RX),
            ('expires', 'eq', '-1'),
            ('pragma', 'eq', 'no-cache'),
            ('cache-control', 'eq', test_utils.NO_CACHE_HEADER),
            ('content-encoding', 'eq', None),
            ('content-length', 'regex', re.compile('[0-9]+')),
            ('content-type', 'eq', 'text/html; charset=utf-8'),
            ('x-xss-protection', 'eq', '0')
          ]

    else:
      self.firefox36.response_headers = [
            ('etag', 'regex', re.compile('"[0-9a-f]{32}"')),
            ('server', 'eq', 'Google Frontend'),
            ('date', 'regex', test_utils.HTTP_DATE_RX),
            ('expires', 'eq', '-1'),
            ('pragma', 'eq', 'no-cache'),
            ('cache-control', 'eq', test_utils.NO_CACHE_HEADER),
            ('content-encoding', 'eq', 'gzip'),
            ('content-length', 'regex', re.compile('[0-9]+')),
            ('content-type', 'eq', 'text/html; charset=utf-8'),
            ('x-xss-protection', 'eq', '0')
          ]

    # Make a special request for the not allowed method tests.
    self.firefox36_not_allowed = test_utils.TestRequest(self.firefox36)
    self.firefox36_not_allowed.response_status = 405

    # The error page is served in simple text/html.
    self.firefox36_not_allowed.response_body = True
    self.firefox36_not_allowed.response_headers[4] = ('pragma', 'eq', None)
    self.firefox36_not_allowed.response_headers[8] = ('content-type', 'eq', 'text/html')
    self.firefox36_not_allowed.response_headers[9] = ('x-xss-protection', 'eq', None)
    self.firefox36_not_allowed.response_headers.append(
        ('allow', 'eq', 'GET, POST, HEAD'))
    self.firefox36_not_allowed.response_headers[0] = ('etag', 'eq', None)

    if test_utils.LOCAL:
      # The dev_appserver autimatically sets the Expires and Cache-Control
      # headers -- annoying.
      self.firefox36_not_allowed.response_headers[3] = (
          'expires', 'eq', 'Fri, 01 Jan 1990 00:00:00 GMT')
      self.firefox36_not_allowed.response_headers[5] = (
          'cache-control', 'eq', 'no-cache')
    else:
      self.firefox36_not_allowed.response_headers[3] = (
          'expires', 'eq', None)
      # And the production server automatically sets the Cache-Control header,
      # but I'm assuming this is because we don't set it in our 405 handler.
      # See issue #28
      self.firefox36_not_allowed.response_headers[5] = (
          'cache-control', 'eq', 'private, x-gzip-ok=""')

  @test_function
  def get(self):
    """GET request for /datastore/subscribers/
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

  @test_function
  def put(self):
    """PUT request for /datastore/subscribers/
    """
    ff36 = test_utils.TestRequest(self.firefox36_not_allowed)
    ff36.body = '<html>Some HTML</html>'
    ff36.headers['Content-Length'] = str(len(ff36.body))
    ff36.headers['Content-Type'] = 'text/html'
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def post(self):
    """POST request for /datastore/subscribers/

    #### TODO
    So far, this is only testing for a response. For complete testing we need
    to finish the functionality of the /datastore/ service and test the data
    integrity issues - read, write, delete, and permissions.

    Complete /datastore/ testing should be put into a dedicated module.
    """
    # Create a random email address, since that is how we distinguish unique
    # subscribers.
    def random_email():
      return hmac.new(
          str(datetime.datetime.utcnow()).encode('ascii'),
          str(random.randint(0, 9999)).encode('ascii'),
          hashlib.sha1).hexdigest()

    # Make a copy of the generic test configs.
    ff36 = test_utils.TestRequest(self.firefox36)
    ff36.headers['Content-Type'] = 'application/x-www-form-urlencoded'

    # Make a copy of the generic test configs for AJAX.
    ff36_ajax = test_utils.TestRequest(ff36)
    ff36_ajax.headers['Accept'] = 'application/json'
    ff36_ajax.headers['X-Requested-With'] = 'XMLHttpRequest'
    ff36_ajax.response_headers[8] = ('content-type', 'eq', 'application/json')

    # Create the new member entity.
    ff36.body = urllib.urlencode({
        'new_subscription': 'Delete Me',
        'email': '%s@example.com'% random_email()
      })
    ff36.headers['Content-Length'] = str(len(ff36.body))
    ff36.response_status = 201

    # Repeat for AJAX
    ff36_ajax.body = urllib.urlencode({
        'new_subscription': 'Delete Me',
        'email': '%s@example.com'% random_email()
      })
    ff36_ajax.headers['Content-Length'] = str(len(ff36_ajax.body))
    ff36_ajax.response_status = 201

    # Make another copy of the test configs to test a form submission with no
    # 'name' data field.
    ff36_nosub = test_utils.TestRequest(ff36)
    ff36_nosub.body = urllib.urlencode({
        'new_subscription': '',
        'email': '%s@example.com'% random_email()
      })
    ff36_nosub.headers['Content-Length'] = str(len(ff36_nosub.body))
    ff36_nosub.response_status = 201

    # Repeat for AJAX
    ff36_nosub_ajax = test_utils.TestRequest(ff36_ajax)
    ff36_nosub_ajax.body = urllib.urlencode({
        'new_subscription': '',
        'email': '%s@example.com'% random_email()
      })
    ff36_nosub_ajax.headers['Content-Length'] = str(len(ff36_nosub_ajax.body))
    ff36_nosub_ajax.response_status = 201

    # Make one more copy of the test configs to test a form submission that is
    # missing the 'email' data field.
    ff36_noemail = test_utils.TestRequest(ff36)
    ff36_noemail.body = urllib.urlencode({
        'name': 'Delete Me'
      })
    ff36_noemail.headers['Content-Length'] = str(len(ff36_noemail.body))
    ff36_noemail.response_status = 409

    # Repeat for AJAX
    ff36_noemail_ajax = test_utils.TestRequest(ff36_ajax)
    ff36_noemail_ajax.body = urllib.urlencode({
        'name': 'Delete Me'
      })
    ff36_noemail_ajax.headers['Content-Length'] = \
        str(len(ff36_noemail_ajax.body))
    ff36_noemail_ajax.response_status = 409

    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    configs.update('firefox36_ajax', ff36_ajax)
    configs.update('firefox36_nosub', ff36_nosub)
    configs.update('firefox36_nosub_ajax', ff36_nosub_ajax)
    configs.update('firefox36_noemail', ff36_noemail)
    configs.update('firefox36_noemail_ajax', ff36_noemail_ajax)
    return configs.items()

  @test_function
  def delete(self):
    """DELETE request for /datastore/subscribers/
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36_not_allowed)
    return configs.items()

  @test_function
  def head(self):
    """HEAD request for /datastore/subscribers/
    """
    ff36 = test_utils.TestRequest(self.firefox36)
    ff36.response_headers[6] = ('content-encoding', 'eq', None)
    ff36.response_headers[7] = ('content-length', 'eq', '0')
    ff36.response_body = None
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def options(self):
    """OPTIONS request for /datastore/subscribers/
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36_not_allowed)
    return configs.items()

  @test_function
  def trace(self):
    """TRACE request for /datastore/subscribers/
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36_not_allowed)
    return configs.items()

class DatastoreSubscribersInvalid(unittest.TestCase):
  """The /datastore/subscribers/ URL must have a '/' on the end of it."""

  url = '/datastore/subscribers'

  def configure(self):
    """Set up the request/response data.

    The test_utils.test_function decorator will cause this method
    to be called once for this test class, but NOT each time a test
    function is called.
    """
    self.firefox36 = test_utils.TestRequest(firefox36_config)
    self.firefox36.response_status = 301
    self.firefox36.response_body = True

    if test_utils.LOCAL:
      self.firefox36.response_headers = [
            ('etag', 'eq', None),
            ('server', 'eq', 'Development/1.0'),
            ('date', 'regex', test_utils.HTTP_DATE_RX),
            ('expires', 'regex', test_utils.HTTP_DATE_RX),
            ('pragma', 'eq', None),
            # Expire in 4 weeks.
            ('cache-control', 'eq', 'public, max-age=2419200'),
            ('content-encoding', 'eq', None),
            ('content-length', 'eq', '295'),
            ('content-type', 'eq', 'text/html; charset=utf-8'),
            ('x-xss-protection', 'eq', '0')
          ]

    else:
      self.firefox36.response_headers = [
            ('etag', 'eq', None),
            ('server', 'eq', 'Google Frontend'),
            ('date', 'regex', test_utils.HTTP_DATE_RX),
            ('expires', 'regex', test_utils.HTTP_DATE_RX),
            ('pragma', 'eq', None),
            # Expire in 4 weeks.
            ('cache-control', 'eq', 'public, max-age=2419200'),
            ('content-encoding', 'eq', 'gzip'),
            ('content-length', 'eq', '232'),
            ('content-type', 'eq', 'text/html; charset=utf-8'),
            ('x-xss-protection', 'eq', '0')
          ]

  @test_function
  def get(self):
    """GET request for /datastore/subscribers Invalid
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

  @test_function
  def put(self):
    """PUT request for /datastore/subscribers Invalid
    """
    ff36 = test_utils.TestRequest(self.firefox36)
    ff36.body = 'User-agent: *\nAllow: /\n'
    ff36.headers['Content-Length'] = str(len(ff36.body))
    ff36.headers['Content-Type'] = 'text/plain'
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def post(self):
    """POST request for /datastore/subscribers Invalid
    """
    ff36 = test_utils.TestRequest(self.firefox36)
    ff36.body = 's=foo&num=44'
    ff36.headers['Content-Length'] = str(len(ff36.body))
    ff36.headers['Content-Type'] = 'application/x-www-form-urlencoded'
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def delete(self):
    """DELETE request for /datastore/subscribers Invalid
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

  @test_function
  def head(self):
    """HEAD request for /datastore/subscribers Invalid
    """
    ff36 = test_utils.TestRequest(self.firefox36)
    ff36.response_headers[6] = ('content-encoding', 'eq', None)
    ff36.response_headers[7] = ('content-length', 'eq', '0')
    ff36.response_body = None
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def options(self):
    """OPTIONS request for /datastore/subscribers Invalid
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

  @test_function
  def trace(self):
    """TRACE request for /datastore/subscribers Invalid
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

class DatastoreActions(unittest.TestCase):
  url = '/datastore/actions/'

  def configure(self):
    """Set up the request/response data.

    The test_utils.test_function decorator will cause this method
    to be called once for this test class, but NOT each time a test
    function is called.
    """
    # Make a copy of the configs.
    self.firefox36 = test_utils.TestRequest(firefox36_config)
    self.firefox36.response_status = 200
    self.firefox36.response_body = True

    if test_utils.LOCAL:
      self.firefox36.response_headers = [
            ('etag', 'regex', re.compile('"[0-9a-f]{32}"')),
            ('server', 'eq', 'Development/1.0'),
            ('date', 'regex', test_utils.HTTP_DATE_RX),
            ('expires', 'eq', '-1'),
            ('pragma', 'eq', 'no-cache'),
            ('cache-control', 'eq', test_utils.NO_CACHE_HEADER),
            ('content-encoding', 'eq', None),
            ('content-length', 'regex', re.compile('[0-9]+')),
            ('content-type', 'eq', 'text/html; charset=utf-8'),
            ('x-xss-protection', 'eq', '0')
          ]

    else:
      self.firefox36.response_headers = [
            ('etag', 'regex', re.compile('"[0-9a-f]{32}"')),
            ('server', 'eq', 'Google Frontend'),
            ('date', 'regex', test_utils.HTTP_DATE_RX),
            ('expires', 'eq', '-1'),
            ('pragma', 'eq', 'no-cache'),
            ('cache-control', 'eq', test_utils.NO_CACHE_HEADER),
            ('content-encoding', 'eq', 'gzip'),
            ('content-length', 'regex', re.compile('[0-9]+')),
            ('content-type', 'eq', 'text/html; charset=utf-8'),
            ('x-xss-protection', 'eq', '0')
          ]

    # Make a special request for the not allowed method tests.
    self.firefox36_not_allowed = test_utils.TestRequest(self.firefox36)
    self.firefox36_not_allowed.response_status = 405

    # The error page is served in simple text/html.
    self.firefox36_not_allowed.response_body = True
    self.firefox36_not_allowed.response_headers[4] = ('pragma', 'eq', None)
    self.firefox36_not_allowed.response_headers[8] = ('content-type', 'eq', 'text/html')
    self.firefox36_not_allowed.response_headers[9] = ('x-xss-protection', 'eq', None)
    self.firefox36_not_allowed.response_headers.append(
        ('allow', 'eq', 'GET, POST, HEAD'))
    self.firefox36_not_allowed.response_headers[0] = ('etag', 'eq', None)

    if test_utils.LOCAL:
      # The dev_appserver autimatically sets the Expires and Cache-Control
      # headers -- annoying.
      self.firefox36_not_allowed.response_headers[3] = (
          'expires', 'eq', 'Fri, 01 Jan 1990 00:00:00 GMT')
      self.firefox36_not_allowed.response_headers[5] = (
          'cache-control', 'eq', 'no-cache')
    else:
      self.firefox36_not_allowed.response_headers[3] = (
          'expires', 'eq', None)
      # And the production server automatically sets the Cache-Control header,
      # but I'm assuming this is because we don't set it in our 405 handler.
      # See issue #28
      self.firefox36_not_allowed.response_headers[5] = (
          'cache-control', 'eq', 'private, x-gzip-ok=""')

  @test_function
  def get(self):
    """GET request for /datastore/actions/
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

  @test_function
  def put(self):
    """PUT request for /datastore/actions/
    """
    ff36 = test_utils.TestRequest(self.firefox36_not_allowed)
    ff36.body = '<html>Some HTML</html>'
    ff36.headers['Content-Length'] = str(len(ff36.body))
    ff36.headers['Content-Type'] = 'text/html'
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def post(self):
    """POST request for /datastore/actions/

    #### TODO
    So far, this is only testing for a response. For complete testing we need
    to finish the functionality of the /datastore/ service and test the data
    integrity issues - read, write, delete, and permissions.

    Complete /datastore/ testing should be put into a dedicated module.
    """
    # Make a copy of the generic test configs.
    ff36 = test_utils.TestRequest(self.firefox36)
    ff36.headers['Accept'] = 'application/json'
    ff36.headers['X-Requested-With'] = 'XMLHttpRequest'
    ff36.response_headers[8] = ('content-type', 'eq', 'application/json')

    # Record some page actions.
    ff36.body = urllib.urlencode({'browser_id': 'testing', 'actions': [
        'clicked on something'
      , 'scrolled somewhere'
      ]})
    ff36.headers['Content-Length'] = str(len(ff36.body))
    ff36.headers['Content-Type'] = 'application/x-www-form-urlencoded'

    ff36.response_status = 200

    # Make another copy of the generic test configs.
    ff36_sansbid = test_utils.TestRequest(ff36)

    # Try to record some page actions.
    ff36.body = urllib.urlencode({'actions': [
        'clicked on something'
      , 'scrolled somewhere'
      ]})
    ff36.headers['Content-Length'] = str(len(ff36.body))
    ff36.headers['Content-Type'] = 'application/x-www-form-urlencoded'

    ff36.response_status = 400

    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    configs.update('firefox36_sansbid', ff36_sansbid)
    return configs.items()

  @test_function
  def delete(self):
    """DELETE request for /datastore/actions/
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36_not_allowed)
    return configs.items()

  @test_function
  def head(self):
    """HEAD request for /datastore/actions/
    """
    ff36 = test_utils.TestRequest(self.firefox36)
    ff36.response_headers[6] = ('content-encoding', 'eq', None)
    ff36.response_headers[7] = ('content-length', 'eq', '0')
    ff36.response_body = None
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def options(self):
    """OPTIONS request for /datastore/actions/
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36_not_allowed)
    return configs.items()

  @test_function
  def trace(self):
    """TRACE request for /datastore/actions/
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36_not_allowed)
    return configs.items()

class DatastoreActionsInvalid(unittest.TestCase):
  """The /datastore/actions/ URL must have a '/' on the end of it."""

  url = '/datastore/actions'

  def configure(self):
    """Set up the request/response data.

    The test_utils.test_function decorator will cause this method
    to be called once for this test class, but NOT each time a test
    function is called.
    """
    self.firefox36 = test_utils.TestRequest(firefox36_config)
    self.firefox36.response_status = 301
    self.firefox36.response_body = True

    if test_utils.LOCAL:
      self.firefox36.response_headers = [
            ('etag', 'eq', None),
            ('server', 'eq', 'Development/1.0'),
            ('date', 'regex', test_utils.HTTP_DATE_RX),
            ('expires', 'regex', test_utils.HTTP_DATE_RX),
            ('pragma', 'eq', None),
            # Expire in 4 weeks.
            ('cache-control', 'eq', 'public, max-age=2419200'),
            ('content-encoding', 'eq', None),
            ('content-length', 'eq', '287'),
            ('content-type', 'eq', 'text/html; charset=utf-8'),
            ('x-xss-protection', 'eq', '0')
          ]

    else:
      self.firefox36.response_headers = [
            ('etag', 'eq', None),
            ('server', 'eq', 'Google Frontend'),
            ('date', 'regex', test_utils.HTTP_DATE_RX),
            ('expires', 'regex', test_utils.HTTP_DATE_RX),
            ('pragma', 'eq', None),
            # Expire in 4 weeks.
            ('cache-control', 'eq', 'public, max-age=2419200'),
            ('content-encoding', 'eq', 'gzip'),
            ('content-length', 'eq', '229'),
            ('content-type', 'eq', 'text/html; charset=utf-8'),
            ('x-xss-protection', 'eq', '0')
          ]

  @test_function
  def get(self):
    """GET request for /datastore/actions Invalid
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

  @test_function
  def put(self):
    """PUT request for /datastore/actions Invalid
    """
    ff36 = test_utils.TestRequest(self.firefox36)
    ff36.body = 'User-agent: *\nAllow: /\n'
    ff36.headers['Content-Length'] = str(len(ff36.body))
    ff36.headers['Content-Type'] = 'text/plain'
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def post(self):
    """POST request for /datastore/actions Invalid
    """
    ff36 = test_utils.TestRequest(self.firefox36)
    ff36.body = 's=foo&num=44'
    ff36.headers['Content-Length'] = str(len(ff36.body))
    ff36.headers['Content-Type'] = 'application/x-www-form-urlencoded'
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def delete(self):
    """DELETE request for /datastore/actions Invalid
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

  @test_function
  def head(self):
    """HEAD request for /datastore/actions Invalid
    """
    ff36 = test_utils.TestRequest(self.firefox36)
    ff36.response_headers[6] = ('content-encoding', 'eq', None)
    ff36.response_headers[7] = ('content-length', 'eq', '0')
    ff36.response_body = None
    configs = test_utils.TestConfig()
    configs.update('firefox36', ff36)
    return configs.items()

  @test_function
  def options(self):
    """OPTIONS request for /datastore/actions Invalid
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

  @test_function
  def trace(self):
    """TRACE request for /datastore/actions Invalid
    """
    configs = test_utils.TestConfig()
    configs.update('firefox36', self.firefox36)
    return configs.items()

