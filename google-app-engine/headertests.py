import sys

def start_response(status, headers, exc_info=None):
  """A start_response() callable as specified by PEP 333"""
  if exc_info is not None:
    raise exc_info[0], exc_info[1], exc_info[2]
  print "Status: %s" % status
  for name, val in headers:
    print "%s: %s" % (name, val)
  print
  return sys.stdout.write

body = 'Lorem ipsum\n'
write = start_response('200 OK', [('Content-Length', len(body))])
write(body)

