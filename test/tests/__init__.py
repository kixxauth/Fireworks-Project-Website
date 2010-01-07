import hashlib
import httplib
import simplejson

HOST = 'localhost'
LOCALHOST = 'localhost'
USERNAME = None
PASSKEY = None

def set_HOST(val):
  global HOST
  HOST = val

def set_LOCALHOST(val):
  global LOCALHOST
  LOCALHOST = val

def set_USERNAME(val):
  global USERNAME
  USERNAME = val

def set_PASSKEY(val):
  global PASSKEY 
  PASSKEY = val

def setupLocalContent():
  if HOST != LOCALHOST:
    return

  code, reason, headers, body = makeRequest(
      method='GET',
      url='/',
      headers={'content-length': 0})

  if code == 200 and len(body) > 100:
    return

  print
  print 'INFO loading remote page content to local dev_appserver'

  code, reason, headers, body = makeRequest(
      host='www.fireworksproject.com',
      method='GET',
      url='/content-manager/configs',
      headers={'content-length': 0})

  configs = simplejson.loads(body)

  for k in configs:
    page_name = configs[k][0]
    code, reason, headers, content = makeRequest(
        host='www.fireworksproject.com',
        method='GET',
        url='/content-manager/pages/%s'% page_name,
        headers={'content-length': 0})

    if code != 200:
      continue

    print 'Loading page %s'% page_name
    post = 'name=%s&content=%s'% (page_name, content)
    code, reason, headers, body = makeRequest(
        method='POST',
        url='/testcontent/',
        body=post,
        headers={'content-length': len(post)})

  print 'Done'
  print

def httpConnection(host=None):
  host = host or HOST
  return httplib.HTTPConnection(host)

def makeRequest(host=None, method='GET', url='/', body=None, headers={}):
  cxn = httpConnection(host)
  cxn.request(method, url, body, headers)
  r = cxn.getresponse()
  headers = r.getheaders()
  body = r.read()
  cxn.close()
  return (r.status, r.reason, headers, body)

def createJSONRequest(method='get', creds=[], body=None):
  """Create the JSON encoded body of a JSONRequest"""
  return simplejson.dumps(dict(
      head=dict(method=method, authorization=creds),
      body=body))

def makeJSONRequest_for_httplib(url='/', method='get', creds=[], body=None):
  """return a tuple that can be unpacked as the arguments to
  httplib.Connection().request()"""
  return ('POST', url,
      createJSONRequest(method, creds, body), getJSONRequestHeaders())

def createCredentials(passkey, username, nonce, nextnonce):
  """Takes passkey, nonce, nextnonce and returns a list;
  [username, cnonce, response]
  """
  def hash(s):
    return hashlib.sha1(s).hexdigest()

  def cnonce(key):
    return hash(hash(key))

  def response(key):
    return hash(key)

  def juxt(passkey, seed):
    return str(passkey) + str(seed)

  return [username,
      cnonce(juxt(passkey, nextnonce)),
      response(juxt(passkey, nonce))]

def makeJSONRequest(url='/', method='get', creds=[]):
  cxn = httpConnection()
  req = makeJSONRequest_for_httplib(
        url=url, method=method, creds=creds)
  cxn.request(*req)
  res = cxn.getresponse().read()
  rv = simplejson.loads(res)
  cxn.close()
  return rv
