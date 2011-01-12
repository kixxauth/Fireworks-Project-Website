#! /usr/bin/env python
"""
    @file FWPWebsite.test.testrunner
    ==========================================
    Command line script to run automated test suites.

    The tests to run are listed in `config.py`. To run all configured tests do

    `./testrunner.py`

    with no parameters or

    `./testrunner.py full`

    to do the same thing.

    To run an individual test suite by name do `./testrunner.py NAME` where
    NAME is the suite name in `config.py`.  For example:

    `./testrunner.py not_found`

    to run the not_found test suite.

    If localhost:8080 is available (the local GAE `dev_appserver`) then the tests
    will be run against the `dev_appserver` but no tests will be run against the
    production environment.

    Consult the Google documentation for the `dev_appserver`:
    http://code.google.com/appengine/docs/python/tools/devserver.html
    
    If localhost:8080 is *not* available, `testrunner.py` will attempt test
    against the staging domain in the production environment
    'VERSION.latest.APPNAME.appspot.com' where VERSION is the application version
    number, and APPNAME is the application name in app.yaml. So, a host 
    might look like this for example:

    `5.latest.fireworkscomputer.appspot.com`

    !Important: If you want to test locally, make sure the
    `dev_appserver` is running. If you want to test the remote production staging
    environment then make sure `dev_appserver` is *not* running.

    It helps to know how GAE makes applications available. This is from the App
    Engine Blog on app versioning:

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

    @author Kris Walker <kixxauth@gmail.com>
    @copyright (c) 2010 - 2011 by The Fireworks Project.
    @license MIT, see MIT-LICENSE for more details.
"""

import sys

import suites
from tests import test_utils

import session

def main():
    host = session.host()
    if host is False:
        raise Exception('no connection to %s or %s'% (localhost, remote_host))

    # Inform the test suites of the host discovery.
    test_utils.setup(host, session.islocal())

    # Get the command line arguments.
    cl_suites = sys.argv[1:]
    if len(cl_suites) is 0:
        cl_suites = ['full']

    # Tell the user we're running.
    print ''
    print 'Running tests on: %s' % host 
    print 'Running suites: %s' % cl_suites
    print ''

    # Run the tests.
    suites.run_suites(cl_suites)

if __name__ == '__main__':
    main()

