#! /usr/bin/env python
"""
  FWPWebsite test.suites
  ~~~~~~~~~~~~~~~~~~~~~~
  Command line script to run test suites.

  The tests to run are listed in `config.py`. To run all configured tests do
    `./testrunner.py`
  with no parameters or
    `./testrunner.py full`
  to do the same thing.

  To run and individual test suite by name run `./testrunner.py NAME` where
  NAME is the suite name in `config.py`.  For example:

    `./testrunner.py not_found`

  will run the not_found test suite.

  If localhost:8080 is available (the local GAE `dev_appserver`) then it will
  be tested against the `dev_appserver` and no tests will be run on the
  production environment.

  Consult the Google documentation for the `dev_appserver`:
  http://code.google.com/appengine/docs/python/tools/devserver.html
  
  If localhost:8080 is *not* available, `testrunner.py` will attempt to contact
  the staging domain in the production environment by testing against
  'VERSION.latest.APPNAME.appspot.com' where VERSION is the application version
  number in app.yaml, and APPNAME is the application name in app.yaml. So, a
  test domain might look like this for example:

    `5.latest.fireworkscomputer.appspot.com`

  !Important: So, if you want to test locally, then make sure the
  `dev_appserver` is running. If you want to test the remote production staging
  environment then make sure `dev_appserver` is not running.

  It helps to know how GAE makes applications available. From the App Engine
  Blog on app versioning:

  "App Engine permits you to deploy multiple versions of your app and have them
  running side-by-side. All the versions share the samedatastore and memcache,
  but they run in separate instances and have different URLs. Your 'live'
  version always serves off yourapp.appspot.com as well as any domains you have
  mapped, but all your app's versions are accessible at
  version.latest.yourapp.appspot.com. Multiple versions are particularly useful
  for testing a new release in a production environment, on real data, before
  making it available to all your users.

  Something that's less known is that the different app versions don't even have
  to have the same runtime! It's perfectly fine to have one version of an app
  using the Java runtime and another version of the same app using the Python
  runtime."
  http://googleappengine.blogspot.com/2009/06/10-things-you-probably-didnt-know-about.html

  (see google_app_engine/app.yaml for more information)

  :copyright: (c) 2010 by The Fireworks Project.
  :license: MIT, see LICENSE for more details.
"""

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

