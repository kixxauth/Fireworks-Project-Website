"""
    @file FWPWebsite.Google_App_Engine.base_handler
    ===============================================
    Contains the BaseHandler class for subclassing handlers in other modules.
    All handlers must be subclasses of `Handler` from the fwerks `fwerks.py`
    module. See `fwerks.py` for documentation regarding request handlers.

    @author Kris Walker <eixxauth@gmail.com>
    @copyright (c) 2010 by The Fireworks Project.
    @license MIT, see MIT-LICENSE for more details.
"""
import logging
import time
import urlparse

from werkzeug import BaseRequest, CommonRequestDescriptorsMixin, AcceptMixin, ETagRequestMixin
from werkzeug import BaseResponse, CommonResponseDescriptorsMixin, ETagResponseMixin
from werkzeug import UserAgent, cached_property

from openid.consumer.consumer import Consumer, FAILURE, SUCCESS, CANCEL
import aeoid_store

import fwerks
import dstore

Handler = fwerks.Handler
User =    fwerks.User

# ### The Beaker session object is stored on the WSGI environs.
# This is the dict key to access the session object.
BEAKER_ENV_KEY = 'beaker.session'

# ### The Beaker session cookie key.
BEAKER_COOKIE_KEY = 'fpsession'

# ### Beaker module configuration options.
beaker_session_configs = {
      'session.type': 'ext:google' # Beaker implements a GAE backend.
    , 'session.key': BEAKER_COOKIE_KEY # The session cookie id.
}

# ### The URL query param used for the federated identifier.
AUTH_REQUEST_FIELD = 'federated_id'

# ### The URL query param signalling a federated login process is active.
AUTH_PROCESS_FIELD = 'federated_authentication'


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
    def user(self):
        """### The `fwerks.User` object for this request on this session.
        """
        session = self.environ.get(BEAKER_ENV_KEY)
        if session is None:
            return

        if 'authenticated' in session:
            # TODO: Check session access time and maybe invalidate or delete an
            # expired session, creating a new one or prompting another login.
            return User(session)

        if self.values.get(AUTH_PROCESS_FIELD) is None:
            return

        # This is a redirected federated login attempt.  If this raises an
        # exception it will be caught by the fwerks dispatcher.
        logging.warn('self.request.url: %s', self.request.url)
        auth_reponse = Consumer( session
                               , aeiod_store.AppEngineStore()
                               ).complete(self.request.args, self.request.url)

        if response.status == SUCCESS:
            session['authenticated'] = True
            return User(session)

        elif response.status in (FAILURE, CANCEL):
            return
        else:
            logging.error('Unexpected error in OpenID authentication: %s', response)


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
            attrs = ( user_agent.platform
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
            browser = dstore.Browser( user_agent=user_agent
                                    , init_path=self.request.path
                                    , init_referrer=self.request.referrer
                                    , init_address=self.request.remote_addr
                                    )
            browser.put()
            browser_id = dstore.browser_key(browser)

        # Reset the browser id cookie
        if status_ok:
            response.set_cookie( 'bid'
                               , value=browser_id
                               , expires=(int(time.time()) + 31556926) # Exp in 1 year.
                               )

        if record_request:
            user_agent = user_agent or self.user_agent_repr
            request = dstore.Request( browser=browser_id
                                    , user_agent=user_agent
                                    , path=self.request.path
                                    , referrer=self.request.referrer
                                    , address=self.request.remote_addr
                                    , status=(response.status_code or 0)
                                    )
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


class AuthRequestHandler(BaseHandler):

    def respond(self, response):
        response.mimetype = 'text/plain'

        # No caching.
        response.headers['Expires'] = 'Fri, 01 Jan 1990 00:00:00 GMT'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Cache-Control'] = NO_CACHE_HEADER

        return self.finalize_response(response)

    def get(self):
        federated_id = self.request.args.get(AUTH_REQUEST_FIELD)
        if not federated_id:
            response = Response()
            # Since we only care about Ajax requests we don't have to do
            # anything more informative than a 409.
            response.status_code = 409
            return self.respond(response)

        session = self.environ.get(BEAKER_ENV_KEY)

        # If this raises an exception it will be caught by the fwerks dispatcher.
        auth_request = Consumer( session
                               , aeiod_store.AppEngineStore()
                               ).begin(federated_id)

        cont = list(urlparse.urlparse(self.args.get('continuation', '/')))
        qstr = AUTH_PROCESS_FIELD +'=true'
        cont[4] = cont[4] and (cont[4] + ('&'+ qstr)) or ('?'+ qstr)

        return_to = urlparse.urljoin( self.request.host
                                    , urlparse.urlunparse(cont)
                                    )

        logging.warn('return_to: %s', return_to)

        redirect_url = auth_request.redirectURL(self.request.host, return_to)
        # The Ajax request wants the redirect url as plain text, not an actual
        # HTTP redirect.
        response = self.respond(Response(redirect_url))
        session.save()
        return response

