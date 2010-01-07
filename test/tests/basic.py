import unittest
import tests

# todo: robots.txt
# todo: favicon
# todo: setup cms for testing on dev_appserver 

class Defaults(unittest.TestCase):
  def test_notFound(self):
    """Check for not found response."""
    cxn = tests.httpConnection()
    cxn.request('GET', '/foo')
    response = cxn.getresponse()
    self.assertEqual(response.status, 404)
    assert len(response.read()) > 30, 'not found body length'
    cxn.close()

  def test_robots(self):
    """Check for robots.txt response."""
    cxn = tests.httpConnection()
    cxn.request('GET', '/robots.txt')
    response = cxn.getresponse()
    self.assertEqual(response.status, 200)
    self.assertEqual(response.read(), 'User-agent: *\nAllow: /\n')
    cxn.close()

  def test_sitemap(self):
    """Check for sitemap.xml response."""
    cxn = tests.httpConnection()
    cxn.request('GET', '/sitemap.xml')
    response = cxn.getresponse()
    self.assertEqual(response.status, 200)
    assert len(response.read()) > 200, 'sitemap.xml body length'
    cxn.close()

# todo: test headers
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

# todo: test images, scripts, styles, downloads, etc.
