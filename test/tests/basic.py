import unittest
import tests

# todo: robots.txt
# todo: favicon
# todo: setup cms for testing on dev_appserver 

class NotFound(unittest.TestCase):
  def test_notFound(self):
    """Check for not found response."""
    cxn = tests.httpConnection()
    cxn.request('GET', '/foo')
    response = cxn.getresponse()
    self.assertEqual(response.status, 404)
    assert len(response.read()) > 100, 'not found body length'
    cxn.close()

# todo: test headers
class StaticHTML(unittest.TestCase):
  methods = ['GET','POST','PUT','DELETE','OPTIONS','HEAD','TRACE']

  def test_home(self):
    """home page html"""
    if tests.HOST is tests.LOCALHOST:
      return

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
    if tests.HOST is tests.LOCALHOST:
      return

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
    if tests.HOST is tests.LOCALHOST:
      return

    requests = zip(self.methods,
        [200, 200, 405, 405, 405, 405, 405])

    for method, status in requests:
      code, reason, headers, body = tests.makeRequest(
          method=method,
          url='/join',
          headers={'content-length': 0})
      self.assertEqual(code, status,
          'got: %s, wanted: %s, for: %s' % (code, status, method))

  def test_projects(self):
    """projects page html"""
    if tests.HOST is tests.LOCALHOST:
      return

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
    if tests.HOST is tests.LOCALHOST:
      return

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
    if tests.HOST is tests.LOCALHOST:
      return

    requests = zip(self.methods,
        [200, 405, 405, 405, 405, 405, 405])

    for method, status in requests:
      code, reason, headers, body = tests.makeRequest(
          method=method,
          url='/projects/dcube',
          headers={'content-length': 0})
      self.assertEqual(code, status,
          'got: %s, wanted: %s, for: %s' % (code, status, method))

# todo: test images, scripts, styles, downloads, etc.
