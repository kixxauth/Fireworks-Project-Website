#! /usr/bin/env python
import sys
import os
import re
import httplib
import simplejson
import yaml

import suites
from tests import test_utils
from tests import teardown

def checkhost(url):
  cxn = httplib.HTTPConnection(url)
  try:
    cxn.request('GET', '/')
    return True
  except httplib.socket.error:
    return False

def getconfigs(dir):
  """Takes the path to the root app directory and returns the current app
  configs as parsed by PyYaml.
  """
  return yaml.load(open(os.path.join(dir, 'app.yaml')))

def make_auth_request(host, username, passkey=None, nonce=None, nextnonce=None):
  if nonce is None or nextnonce is None or passkey is None:
    creds = (username, )
  else:
    creds = test_utils.create_credentials(passkey, username, nonce, nextnonce)

  cxn = httplib.HTTPConnection(host)
  cxn.request('GET', '/content-management/', '', {
        'User-Agent': 'UA:DCube test :: Auth sys-admin',
        'Authorization': ('Digest qop="chap" realm="fireworksproject.com" '
                          'username="%s" response="%s" cnonce="%s"' % creds),
        'Content-Length': 0,
        'Accept': '*/*'})
  response = cxn.getresponse()
  cxn.close()

  auth_header = response.getheader('WWW-Authenticate', None)
  if auth_header is None:
    auth_header = response.getheader('Authentication-Info', None)

  assert auth_header, \
      'No Authentication header available in the server response.'

  assert response.status is 200 or response.status is 401, \
      'Unexpected HTTP status code (%d) on login.'% response.status

  creds = dict(re.compile('(\w+)[=] ?"?(\w+)"?').findall(auth_header))

  if creds.get('username') is None:
    return False, None, None, None

  if creds.get('nonce') is None:
    return False, username, None, None

  auth = response.status is 200 and True or False
  nonce = creds.get('nonce')
  nextnonce = creds.get('nextnonce')
  return auth, username, nonce, nextnonce


def prompt_username():
  un = raw_input('admin username: ')
  if len(un) < 1:
    print 'username must be more than 0 characters'
    return prompt_username()
  return un

def prompt_passkey(username):
  import getpass
  pk = getpass.getpass('passkey for %s: '% username)
  if len(pk) < 1:
    print 'passkey must be more than 0 characters'
    return prompt_passkey()
  return pk

def authenticate(host):
  username = prompt_username()
  auth, username_, nonce, nextnonce = make_auth_request(host, username)
  if username_ is None:
    return None, None

  assert nonce and nextnonce, 'Missing nonce or nextnonce.'
  passkey = prompt_passkey(username)
  auth, username_, nonce, nextnonce = \
      make_auth_request(host, username, passkey, nonce, nextnonce)

  if not auth:
    return username, None

  return username, passkey

def main():
  localhost = 'localhost:8080'
  passkey = 'secret$key'

  appconfigs = getconfigs(
      os.path.join(
        os.path.split(
          os.path.split(os.path.abspath(__file__))[0])[0],
        'google-app-engine'))

  remote_host = (str(appconfigs.get('version')) +'.latest.'+
                 appconfigs.get('application') +'.appspot.com')

  if checkhost(localhost):
    host = localhost
    cxn = httplib.HTTPConnection(localhost)
    cxn.request('PUT', '/testsetup', None, {'Content-Length':0})
    response = cxn.getresponse()
    assert response.status == 200, \
        'Test user was not setup (status: %d)'% response.status
    temp_test_admin = response.read().rstrip()
    assert isinstance(temp_test_admin, basestring), \
        'Temp username is not a string ().'% temp_test_admin

  elif checkhost(remote_host):
    host = remote_host
    # TODO: Temp assignment.
    temp_test_admin = None
    # temp_test_admin, passkey = authenticate(host)
    # if temp_test_admin is None:
    #   print 'User does not exist.'
    #   exit()
    # if passkey is None:
    #   print 'Invalid passkey... exit()'
    #   exit()

  else:
    raise Exception('no connection to %s or %s'% (localhost, remote_host))

  test_utils.setup(host, (host is localhost), temp_test_admin, passkey)

  suites_ = sys.argv[1:]
  if len(suites_) is 0:
    suites_ = ['full']

  print ''
  print 'Running tests on: %s' % host 
  print 'Running suites: %s' % suites_
  print 'Using admin account for: %s'% temp_test_admin
  print ''

  suites.run_suites(suites_)

  # Teardown insecure user created for testing.
  try:
    teardown.teardown()
  except Exception, e:
    print ''
    print 'Error in teardown: %s'% e
    print ''
  # If you remove this bit of functionality, I will shoot you.
  if host is localhost:
    # Teardown local sys_admin user.
    cxn = httplib.HTTPConnection(localhost)
    cxn.request('DELETE', '/testsetup')
    response = cxn.getresponse()
    assert response.status == 204, \
        'TEST USER WAS NOT DELETED (http status:%d)'% response.status

if __name__ == '__main__':
  main()
