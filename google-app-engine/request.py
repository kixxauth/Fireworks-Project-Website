
import os
import sys
import time

from rfc822 import formatdate

# our config settings
import config

import store

from google.appengine.ext import webapp

def out(status, headers, body):
  print "Status: %s" % ('%d %s' %
      (status, webapp.Response.http_status_message(status)))
  for name, val in headers:
    print "%s: %s" % (name, val)
  print
  # todo: Should we append a newline '\n'??
  sys.stdout.write(body)
  return status, headers, body

def put_new_page(path, version, identity, body):
  page = store.Page(path=path, version=version)
  page.identities = [identity]
  contents = [body]

def handle_put(path, pages):
  parts = path.split('/')
  version = parts[-2]
  identity = parts[-1]

  try:
    body = sys.stdin.read(int(os.environ['CONTENT_LENGTH']))
  except ValueError:
    body = ''

  if len(pages) is 0:
    put_new_page(path, version, identity, body)
    out(201, [], '')
    return

  out(400, [], 'illegal PUT')

def main():
  path = os.environ['PATH_INFO']
  method = os.environ['REQUEST_METHOD']

  pages = store.Page.all().filter('path =', path).order('version').fetch(500)

  if method == 'PUT':
    handle_put(path, pages)
    return

  if len(pages):
    out(200, [
      ('Cache-Control', 'public'),
      ('Expires', formatdate(time.time() + (604800 * 8)))],
      'got version %d'% pages[0].version)
    return

  # Return 'Not Found' response.
  out(404, [
    ('Cache-Control', 'public'),
    # Expires in 8 weeks.
    ('Expires', formatdate(time.time() + (604800 * 8)))],
    'Could not find url %s%s'% (os.environ['HTTP_HOST'], path))
  return

if __name__ == "__main__":
  main()

