"""
    @file FWPWebsite.Google_App_Engine.simple_handlers
    ==================================================
    Contains the SimpleHandler class for basic web page requests.  All handlers
    must be subclasses of `Handler` from the fwerks `fwerks.py` module. See
    `fwerks.py` for documentation regarding request handlers.

    @author Kris Walker <kixxauth@gmail.com>
    @copyright (c) 2010 by The Fireworks Project.
    @license MIT, see MIT-LICENSE for more details.
"""

import os
import time

from google.appengine.api import users
from werkzeug import cached_property

from fwerks import Handler
import utils
import base_handler

render_template = utils.render_template

Response    = base_handler.Response
BaseHandler = base_handler.BaseHandler

class SimpleHandler(BaseHandler):
    """General request handling class for web pages.

    This class is designed and written to be used by the fwerks module.  It
    handles typical GET and HEAD requests. Instances of this class return a
    response by rendering a template matching the name property of this instance.
    See [FWPWebsite.Google_App_Engine.fwerks.Handler] for more info about this.
    """

    def get(self):
        """Accept the HTTP GET method."""
        # Prepare the response.
        response = self.set_default_headers(Response(render_template(self.name)))
        response.mimetype = 'text/html'

        # Expire in 4 days.
        response.expires = int(time.time()) + (86400 * 4)

        return self.finalize_response(response)

    def head(self):
        """Accept the HTTP HEAD method."""
        return self.get()


class ShowEnvirons(Handler):
    """Show the CGI environment variables in human readable form.
    """

    # TODO: Remove this after #12 is fixed.
    @cached_property
    def request(self):
        """### Werkzeug request object.

        This property is lazily created and cached the first time it is
        accessed.
        """
        return base_handler.Request(self.environ)
    
    def get(self):
        """Handler class for '/cgi-env' URL.

        This handler simply prints the CGI environment vars in plain text
        format.
        """
        rv = ''
        for name in os.environ.keys():
            rv += ('%s = %s\n'% (name, os.environ[name]))

        response = Response(rv)
        response.mimetype = 'text/plain'
        return response


class TestException(Handler):
    """Handler class for '/exception' URL.

    Designed to be used to test how the live server responds in the case of an
    exception.
    """
    def get(self):
        assert False, 'Test Exception Raised!'
