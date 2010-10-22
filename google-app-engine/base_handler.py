"""
    @file FWPWebsite.Google_App_Engine.base_handler
    ===============================================
    Contains the BaseHandler class for subclassing handlers in other modules.
    All handlers must be subclasses of `Handler` from the fwerks `fwerks.py`
    module. See `fwerks.py` for documentation regarding request handlers.

    @author Kris Walker <kixxauth@gmail.com>
    @copyright (c) 2010 by The Fireworks Project.
    @license MIT, see LICENSE for more details.
"""
import time

from werkzeug import BaseRequest, CommonRequestDescriptorsMixin, AcceptMixin, ETagRequestMixin
from werkzeug import BaseResponse, CommonResponseDescriptorsMixin, ETagResponseMixin
from werkzeug import UserAgent, cached_property

from fwerks import Handler
import dstore

class Request(BaseRequest, CommonRequestDescriptorsMixin, AcceptMixin, ETagRequestMixin):
  """Request class implementing the following Werkzeug mixins:
  ------------------------------------------------------------

  * `CommonRequestDescriptorsMixin` for various HTTP descriptors.
  * `AcceptMixin` for the HTTP Accept header.
  * `ETagRequestMixin` for easier ETag access.

  See the werkzeug
  [wrapper documentation](http://werkzeug.pocoo.org/documentation/0.6.2/wrappers.html)
  for more information about Request objects and the methods and properties
  available.
  """

class Response(BaseResponse, CommonResponseDescriptorsMixin, ETagResponseMixin):
  """Response class implementing the following Werkzeug mixins:
  -------------------------------------------------------------

  * `CommonResponseDescriptorsMixin` for various HTTP descriptors.
  * `ETagResponseMixin` ETag and conditional response utilities.

  See the werkzeug
  [wrapper documentation](http://werkzeug.pocoo.org/documentation/0.6.2/wrappers.html)
  for more information about Request objects and the methods and properties
  available.
  """

class BaseHandler(Handler):
  """The handler class that most other handlers inherit from.
  -----------------------------------------------------------

  The main purpose of this class is to properly handle and persist our
  analytical data for the website before the response is returned to the
  client.
  """

  @cached_property
  def request(self):
    """### Werkzeug request object.

    This property is lazily created and cached the first time it is accessed.
    """
    return Request(self.environ)

  @cached_property
  def no_persist(self):
    """### Detect the `x-request-no-persist` header.

    The `x-request-no-persist` request header is used by a client to indicate that
    analytics data should not actually be persisted. This is handy for testing.
    """
    rv = self.request.headers.get('x-request-no-persist', None)
    return (rv and rv == 'true') and True or False

  @cached_property
  def user_agent_repr(self):
    """### String representation of the user agent suitable for the datastore.

    The returned string is of the form `platform;browser;version;language`.
    """
    user_agent = UserAgent(self.request.environ)
    if user_agent.browser:
      attrs = (
            user_agent.platform
          , user_agent.browser
          , user_agent.version
          , user_agent.language
          )
      return '%s;%s;%s;%s'% attrs
    return user_agent.string

  @classmethod
  def set_default_headers(cls, response):
    """Helper to quickly set some default headers.

    @param {object} response: The Werkzeug Response object.
    @returns {object}: The Werkzeug Response object.
    """
    # We don't want IE munging our response, so we set X-XSS-Protection to 0
    response.headers['X-XSS-Protection'] = '0'
    return response

  def finalize_response(self, response, record_request=True):
    """Handle and persist analytics data.

    @param {object} response: The Werkzeug Response object.
    @param {bool} record_request: Should this request be persisted?
    @returns {object}: A WSGI callable response object.

    If a 'bid' cookie (browser id) has not been set on this browser, we record
    the new browser in the datastore and set a bid cookie on this browser for
    future use. If the response is not an HTTP error, we set the cookie to expire
    a year from now.

    If `record_request` is True, we persist this request meta data in the datastore and
    reset the 'rid' (request id) cookie on the browser; which will expire at the end of
    the browser session.

    The cache header is set to tell the browser to cache the returned page for
    4 days and keep an ETag for it. Lastly, we conditionally return a response
    body only if the ETag is not a match.
    """
    browser_id = self.request.cookies.get('bid')
    browser = None
    request = None
    user_agent = None
    status = response.status_code 
    status_ok = status >= 200 and status < 300 or status is 304

    # Used to avoid datastore writes during automated testing.
    no_persist = self.no_persist

    response = self.set_default_headers(response)

    # TODO
    #if not browser_id:
      # We also send the browser_id as an ETag in some cases
      #etags = self.request.if_none_match
      #etag = len(etags) and etags.pop() or None
      # If ETag length > 32 (md5) it is a browser key and not a real ETag
      #browser_id = len(etag) > 32 and etag or None
    if not browser_id:
      user_agent = self.user_agent_repr
      browser = dstore.Browser(user_agent=user_agent
                             , init_path=self.request.path
                             , init_referrer=self.request.referrer
                             , init_address=self.request.remote_addr)
      browser.put()
      browser_id = dstore.browser_key(browser)

    # Reset the browser id cookie
    if status_ok:
      response.set_cookie('bid',
                          value=browser_id,
                          expires=(int(time.time()) + 31556926)) # Exp in 1 year.

    if record_request:
      user_agent = user_agent or self.user_agent_repr
      request = dstore.Request(browser=browser_id
                             , user_agent=user_agent
                             , path=self.request.path
                             , referrer=self.request.referrer
                             , address=self.request.remote_addr
                             , status=(response.status_code or 0))
      k = request.put()
      if status_ok:
        response.set_cookie('rid', value=str(k))

    # Delete during automated testing.
    if browser and no_persist:
      browser.delete()
    if request and no_persist:
      request.delete()

    # Caching is private since we're always setting a cookie.
    response.headers['Cache-Control'] = 'private, max-age=%d' % (86400 * 4)

    # Do this last for an accurate conditional response.
    response.add_etag()

    # Only send a response body if the E-Tag does not match.
    return response.make_conditional(self.request)

