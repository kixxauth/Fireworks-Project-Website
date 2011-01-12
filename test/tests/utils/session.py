"""
    @file FWPWebsite.test.session
    =============================
    This module provides a set of singleton (cached) properties for a single testing session.

    @author Kris Walker <kixxauth@gmail.com>
    @copyright (c) 2011 by The Fireworks Project.
    @license MIT, see MIT-LICENSE for more details.
"""

import os

import httplib
import yaml

TEST_DIR      = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR   = os.path.split(TEST_DIR)[0]
GAE_DIR       = os.path.join(PROJECT_DIR, 'google-app-engine')
APP_CONF_PATH = os.path.join(GAE_DIR, 'app.yaml')

localhost = 'localhost:8080'

class computed_value(object):
    """Decorator for caching the results of computed values.
    """
    def __init__(self, fn):
        self.fn = fn;
        self.exec_once = False

    def __call__(self):
        if self.exec_once:
            return self.val

        self.val = self.fn()
        self.exec_once = True
        return self.val

def checkhost(url):
    """Determines if a host is online.

    Makes a call to the given host URL and returns True if it is available and
    False if not.
    """
    cxn = httplib.HTTPConnection(url)
    try:
        cxn.request('GET', '/', None, {'User-Agent': 'testing'})
        return True
    except httplib.socket.error:
        return False

@computed_value
def app_configs():
    """Get the application configuration data.
    
    Takes the path to the root app directory and returns the current app
    configs as parsed by PyYaml.
    """
    return yaml.load(open(APP_CONF_PATH))

@computed_value
def remote_host():
    """Get the name of the remote host.

    Return the host name as configured by tha application id and version number.
    """
    app = app_configs()
    version = str(app.get('version'))
    appid = app.get('application')
    return '%s.latest.%s.appspot.com'% (version, appid)

@computed_value
def host():
    """Get the name of the running host.

    If the localhost is running, it will be returned. If not, check to see if
    the remote host is running and return it if it is. If neither are running,
    boolean False is returned.
    """
    if checkhost(localhost):
        return localhost

    remote = remote_host()
    if checkhost(remote):
        return remote

    return False

@computed_value
def islocal():
    """Check to see if this session is running on the localhost.

    Returns boolean True or False
    """
    return (host() is localhost)

