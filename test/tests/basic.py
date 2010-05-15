import unittest
import test_utils

# TODO: robots.txt
# TODO: favicon

class Defaults(unittest.TestCase):
  def test_notFound(self):
    """Check for not found response."""
    response = test_utils.make_http_request(
        method='GET',
        url='/lost_city_of_atlantis',
        body=None,
        headers={'User-Agent':'testing :: not found',
                 'Content-Length': 0,
                 'Host': test_utils.HOST})
    self.assertEqual(response.status, 404)
    assert len(response.body) > 30, 'not found body length'

  def test_robots(self):
    """Check for robots.txt response."""
    response = test_utils.make_http_request(
        method='GET',
        url='/robots.txt',
        body=None,
        headers={'User-Agent':'testing :: Google verification',
                 'Content-Length': 0,
                 'Host': test_utils.HOST})
    self.assertEqual(response.status, 200)
    self.assertEqual(response.body, 'User-agent: *\nAllow: /\n')

  def test_sitemap(self):
    """Check for sitemap.xml response."""
    response = test_utils.make_http_request(
        method='GET',
        url='/sitemap.xml',
        body=None,
        headers={'User-Agent':'testing :: Google verification',
                 'Content-Length': 0,
                 'Host': test_utils.HOST})
    self.assertEqual(response.status, 200)
    # TODO: the sitemap.xml test should be exactly character for character
    assert len(response.body) > 200, 'sitemap.xml body length'

  def test_goog_verify(self):
    """Check for google verification response."""
    response = test_utils.make_http_request(
        method='GET',
        url='/googlef734612d306d87e6.html',
        body=None,
        headers={'User-Agent':'testing :: Google verification',
                 'Content-Length': 0,
                 'Host': test_utils.HOST})
    self.assertEqual(response.status, 200)
    self.assertEqual(response.body, 'google-site-verification: googlef734612d306d87e6.html')

# TODO: test headers
class StaticHTML(unittest.TestCase):
  methods = ['GET','POST','PUT','DELETE','OPTIONS','HEAD','TRACE']

  def test_home(self):
    """home page html"""
    requests = zip(self.methods,
        [200, 405, 405, 405, 405, 405, 405])

    for method, status in requests:
      code, reason, headers, body = tests.makeRequest(
          method=method,
          url='/',
          headers={'content-length': 0})
      self.assertEqual(code, status,
          'got: %s, wanted: %s, for: %s' % (code, status, method))

  def test_about(self):
    """about page html"""
    requests = zip(self.methods,
        [200, 405, 405, 405, 405, 405, 405])

    for method, status in requests:
      code, reason, headers, body = tests.makeRequest(
          method=method,
          url='/about',
          headers={'content-length': 0})
      self.assertEqual(code, status,
          'got: %s, wanted: %s, for: %s' % (code, status, method))

  def test_join(self):
    """join page html"""
    requests = zip(self.methods,
        [200, 200, 405, 405, 405, 405, 405])

    for method, status in requests:
      if method == 'POST':
        body = 'name=automatedtest'
      else:
        body = ''

      code, reason, headers, body = tests.makeRequest(
          method=method,
          url='/join',
          body=body,
          headers={'content-length': len(body)})
      self.assertEqual(code, status,
          'got: %s, wanted: %s, for: %s' % (code, status, method))

  def test_projects(self):
    """projects page html"""
    requests = zip(self.methods,
        [200, 405, 405, 405, 405, 405, 405])

    for method, status in requests:
      code, reason, headers, body = tests.makeRequest(
          method=method,
          url='/projects',
          headers={'content-length': 0})
      self.assertEqual(code, status,
          'got: %s, wanted: %s, for: %s' % (code, status, method))

    for method, status in requests:
      code, reason, headers, body = tests.makeRequest(
          method=method,
          url='/projects/',
          headers={'content-length': 0})
      self.assertEqual(code, status,
          'got: %s, wanted: %s, for: %s' % (code, status, method))

  def test_projects_kixx(self):
    """projects/kixx page html"""
    requests = zip(self.methods,
        [200, 405, 405, 405, 405, 405, 405])

    for method, status in requests:
      code, reason, headers, body = tests.makeRequest(
          method=method,
          url='/projects/kixx',
          headers={'content-length': 0})
      self.assertEqual(code, status,
          'got: %s, wanted: %s, for: %s' % (code, status, method))

  def test_projects_dcube(self):
    """projects/dcube page html"""
    requests = zip(self.methods,
        [200, 405, 405, 405, 405, 405, 405])

    for method, status in requests:
      code, reason, headers, body = tests.makeRequest(
          method=method,
          url='/projects/dcube',
          headers={'content-length': 0})
      self.assertEqual(code, status,
          'got: %s, wanted: %s, for: %s' % (code, status, method))

class TestContent(unittest.TestCase):
  def test_testcontent(self):
    """testcontent page html"""
    expected_code = None
    if tests.HOST != tests.LOCALHOST:
      expected_code = 403

    body = 'helloWorld'
    code, reason, headers, body = tests.makeRequest(
        method='POST',
        url='/testcontent/',
        body=body,
        headers={'content-length': len(body)})
    self.assertEqual(code, expected_code or 409)
    if tests.HOST is tests.LOCALHOST:
      self.assertEqual(body, 'invalid post data "helloWorld="')

    body = 'name=automatedtest&content=thisIsFoo'
    code, reason, headers, body = tests.makeRequest(
        method='POST',
        url='/testcontent/',
        body=body,
        headers={'content-length': len(body)})
    self.assertEqual(code, expected_code or 204)

# TODO: test images, scripts, styles, downloads, etc.

