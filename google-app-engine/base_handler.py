import time

from werkzeug import BaseRequest, CommonRequestDescriptorsMixin, AcceptMixin, ETagRequestMixin
from werkzeug import BaseResponse, CommonResponseDescriptorsMixin, ETagResponseMixin
from werkzeug import UserAgent, cached_property

from fwerks import Handler
import dstore

class Request(BaseRequest, CommonRequestDescriptorsMixin, AcceptMixin, ETagRequestMixin):
  """Request class implementing the following Werkzeug mixins:

      - :class:`CommonRequestDescriptorsMixin` for various HTTP descriptors.
      - :class:`AcceptMixin` for the HTTP Accept header.
      - :class:`ETagRequestMixin` for easier ETag access.
  """

class Response(BaseResponse, CommonResponseDescriptorsMixin, ETagResponseMixin):
  """Response class implementing the following Werkzeug mixins:

      - :class:`CommonResponseDescriptorsMixin` for various HTTP descriptors.
      - :class:`ETagResponseMixin` ETag and conditional response utilities.
  """

class BaseHandler(Handler):

  @cached_property
  def request(self):
    return Request(self.environ)

  @cached_property
  def no_persist(self):
    rv = self.request.headers.get('x-request-no-persist', None)
    return (rv and rv == 'true') and True or False

  @cached_property
  def user_agent_repr(self):
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
    """
    # We don't want IE munging our response, so we set
    # X-XSS-Protection to 0
    response.headers['X-XSS-Protection'] = '0'
    return response

  def finalize_response(self, response, record_request=True):
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

