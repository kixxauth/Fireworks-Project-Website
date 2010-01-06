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

def httpConnection():
  return httplib.HTTPConnection(HOST)

def makeRequest(method='GET', url='/', body=None, headers={}):
  cxn = httpConnection()
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
