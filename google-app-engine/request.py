
import os
import sys
import time
import datetime
import hashlib
import hmac
import random

import logging

import config
import store

from werkzeug import utils, parse_dict_header

NO_CACHE_HEADER = 'no-cache, no-store, must-revalidate, pre-check=0, post-check=0'

def start_response(status, headers, exc_info=None):
  """A start_response() callable as specified by PEP 333"""
  if exc_info is not None:
    raise exc_info[0], exc_info[1], exc_info[2]
  print "Status: %s" % status
  for name, val in headers:
    print "%s: %s" % (name, val)
  print
  return sys.stdout.write

def out(status, headers, body='', mime='text/html'):
  """Output HTTP response

      This function automatically sets the following headers:
        Content-Type: according to the given mime argument
        X-XSS-Protection: 0

      Note that GAE automatically sets the following headers:
        Cache-Control: to 'no-cache' ! But, only on the dev_appserver

      And GAE does not allow setting the following headers:
        Content-Encoding
        Date
        Server
        Transfer-Encoding
  """
  if isinstance(body, unicode):
    body = body.encode('utf-8')

  headers += [('Content-Length', len(body)), ('Content-Type', mime)]
  logging.warn('-> Headers %s', headers)

  status = ('%d %s' % (status, HTTP_STATUS_CODES[status]))
  write = start_response(status, headers)
  write(body)

def out_405(allowed, headers):
  """Special output function for 405 response.
  """
  headers.append(('Allowed', ', '.join(allowed)))
  out(405, headers, '')

def create_nonce(username):
  """Utility used to create unique, un-guessable strings."""
  k = str(datetime.datetime.utcnow()) + username
  s = str(random.randint(0, 9999))
  return hmac.new(k.encode('ascii'), s.encode('ascii'), hashlib.sha1).hexdigest()

def isempty(x):
  if x is None:
    return True
  if isinstance(x, basestring) or isinstance(x, list):
    return len(x) is 0
  return False

def make_auth_header(username=None, nonce=None, nextnonce=None):
  if isempty(username):
    return 'advanced'

  hstr = 'advanced username="%s", nonce="%s", nextnonce="%s"'
  return hstr % (username, nonce, nextnonce)

def authenticate(header):
  """Take the CHAP credentials of a user and try to authenticate.

  Args:
    creds: The special x-chap header string.
  Returns:
    A tuple of user entity, status code, x-chap response header string,
    and a status message.

  Raises:
    AssertionError: If the user entity was not property created.

  """
  if isempty(header):
    return None, 401, make_auth_header(), 'Missing "x-chap" header.'

  auth = parse_dict_header(header)

  if isempty(auth):
    return None, 401, make_auth_header(), 'Invalid "x-chap" header.'

  username = auth['username']
  if isempty(username):
    return None, 401, make_auth_header(), 'Missing username in "x-chap" header.'

  # Get the user object from the datastore.
  user = store.BaseUser.get(username)

  if user is None:
    return None, 401, make_auth_header(), 'User "%s" not found.' % username

  # This scenario should actually never happen.
  # So we use an assert here.
  assert user.nonce and user.nextnonce, \
      'The user %s has not been created by an admin.' % user.username

  if isempty(auth['response']) or isempty(auth['cnonce']):
    return (user, 401,
        make_auth_header(username, user.nonce, user.nextnonce),
        'Response and cnonce required.')

  # No stored passkey: setting or re-setting the passkey.
  if isempty(user.passkey):
    user.passkey = user.cnonce
    user.nonce = user.nextnonce
    user.nextnonce = create_nonce(user.username)
    user.put()
    return (user, 200,
        make_auth_header(username, user.nonce, user.nextnonce),
        'OK')

  # Now that we know we have a passkey, nonce, and nextnonce for the user we
  # have to make sure that the client has mutated nonce and nextnonce into
  # response and cnonce with user's passkey.
  if auth['cnonce'] == hashlib.sha1(
      hashlib.sha1(user.nextnonce).hexdigest()).hexdigest() \
          or auth['response'] == hashlib.sha1(user.nonce).hexdigest():
    return (user, 401,
        make_auth_header(username, user.nonce, user.nextnonce),
        'Cnonce and response strings must be computed.')

  # Authenticate.
  if hashlib.sha1(auth['response']).hexdigest() != user.passkey:
    return (user, 401,
        make_auth_header(username, user.nonce, user.nextnonce),
        'Denied.')

  # OK
  user.passkey = user.cnonce
  user.nonce = user.nextnonce
  user.nextnonce = create_nonce(user.username)
  user.put()
  return (user, 200,
      make_auth_header(username, user.nonce, user.nextnonce),
      'OK')

def handle_user_request():
  if username == auth_user.username:
    target_user = auth_user
  else:
    target_user = store.BaseUser.get(username)

def handle_management_users(method, username, auth_user, auth_header):
  """Handle a /content-management/users/* URL.
  """
  if not isempty(username):
    handle_user_request(method, username, auth_user, auth_header)
    return

  if method != 'GET':
    # /content-management/users/ only accepts GET requests.
    out_405(['GET'], [('x-chap', auth_header)])
    return

  out(200, [('x-chap', auth_header)], 'user list')


def handle_management(path_parts, method):
  """Handle a /content-management/* URL.
  """
  req = Request(dict(os.environ))

  user, status, auth_header, message = authenticate(req.headers.get('x-chap'))

  if status != 200:
    out(status, [('x-chap', auth_header)], message)
    return

  if len(path_parts) > 1 and path_parts[1] == 'users':
    # Handle a /content-management/users/* URL.
    handle_management_users(method, path_parts[2], user, auth_header)
    return

  out(200, [], 'w00t! %r' % message)

def main():
  env = dict(os.environ)
  path = env['PATH_INFO']
  path_parts = path[1: -1].split('/')
  method = env['REQUEST_METHOD']

  if len(path_parts) > 0 and path_parts[0] == 'content-management':
    # Handle a /content-management/* URL.
    handle_management(path_parts, method)
    return

  pages = store.Page.all().filter('path =', path).order('version').fetch(500)

  if len(pages):
    out(200, [
      ('Cache-Control', 'public'),
      ('Expires', utils.http_date(time.time() + (604800 * 8)))],
      'got version %d'% pages[0].version)
    return

  # Return 'Not Found' response.
  if method == 'HEAD':
    body = ''
  else:
    body = 'Could not find url %s%s\n'% (os.environ['HTTP_HOST'], path)

  out(404, [('Cache-Control', NO_CACHE_HEADER), ('Expires', '-1')], body, 'text/plain')
  return

if __name__ == "__main__":
  main()

