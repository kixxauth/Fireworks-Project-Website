import time

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


class TestException(Handler):
  """Handler class for '/exception' URL.

  Designed to be used to test how the live server responds in the case of an
  exception.
  """
  def get(self):
    assert False, 'Test Exception Raised!'
