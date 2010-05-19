#! /usr/bin/env python
import sys
import os
import httplib
import yaml

import suites
from tests import test_utils

def checkhost(url):
  """Determines if a host is online.

  Makes a call to the given host URL and returns True if it is available and
  False if not.
  """
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

def main():
  # The the path to the app.yaml file and parse it.
  appconfigs = getconfigs(
      os.path.join(
        os.path.split(
          os.path.split(os.path.abspath(__file__))[0])[0],
        'google-app-engine'))

  # Set the host names.
  localhost = 'localhost:8080'
  remote_host = (str(appconfigs.get('version')) +'.latest.'+
                 appconfigs.get('application') +'.appspot.com')

  if checkhost(localhost):
    host = localhost
  elif checkhost(remote_host):
    host = remote_host
  else:
    raise Exception('no connection to %s or %s'% (localhost, remote_host))

  # Inform the test suites of the host discovery.
  test_utils.setup(host, (host is localhost))

  # Get the command line arguments.
  suites_ = sys.argv[1:]
  if len(suites_) is 0:
    suites_ = ['full']

  # Tell the user we're running.
  print ''
  print 'Running tests on: %s' % host 
  print 'Running suites: %s' % suites_
  print ''

  # Run the tests.
  suites.run_suites(suites_)

if __name__ == '__main__':
  main()

