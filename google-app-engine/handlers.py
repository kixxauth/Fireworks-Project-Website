"""
  FWPWebsite.handlers
  ~~~~~~~~~~~~~~~~~~~
  WSGI application request handlers for FWerks (see fwerks.py for more info)
  which use the Werkzeug utilities. All handlers must be subclasses of
  `Handler` from the fwerks `fwerks.py` module. See `fwerks.py` for
  documentation regarding request handlers.

  Werkzeug Response and Request objects are exposed to request handlers and the
  documentation for those Werkzeug classes is at
  http://werkzeug.pocoo.org/documentation/0.6.2/wrappers.html (The source code
  can be found in `werkzeug/wrappers.py`.

  :copyright: (c) 2010 by The Fireworks Project.
  :license: MIT, see LICENSE for more details.
"""

import os
import time
import logging

import utils
from fwerks import Handler
from werkzeug.utils import http_date, cached_property
from werkzeug.exceptions import InternalServerError
from werkzeug.useragents import UserAgent

from django.utils import simplejson

from google.appengine.ext import db
import dstore

from google.appengine.api import mail

# Standard 'Do not cache this!' declaration for the cache-control header.
NO_CACHE_HEADER = 'no-cache, no-store, must-revalidate, pre-check=0, post-check=0'

# Determine if we are running locally or not.
ON_DEV_SERVER = os.environ['SERVER_SOFTWARE'].startswith('Development')

def set_default_headers(response):
  """Helper to quickly set some default headers.
  """
  # We don't want IE munging our response, so we set
  # X-XSS-Protection to 0
  response.headers['X-XSS-Protection'] = '0'
  return response

class BaseHandler(Handler):

  @cached_property
  def no_persist(self):
    rv = self.request.headers.get('x-request-no-persist', None)
    return (rv and rv == 'true') and True or False

  @cached_property
  def persist_user_agent(self):
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

  def finalize_response(self, response, record_request=True):
    browser_id = self.request.cookies.get('bid')
    browser = None
    request = None
    user_agent = None
    status = response.status_code 
    status_ok = status >= 200 and status < 300 or status is 304

    # Used to avoid datastore writes during automated testing.
    no_persist = self.no_persist

    response = set_default_headers(response)

    # TODO
    #if not browser_id:
      # We also send the browser_id as an ETag in some cases
      #etags = self.request.if_none_match
      #etag = len(etags) and etags.pop() or None
      # If ETag length > 32 (md5) it is a browser key and not a real ETag
      #browser_id = len(etag) > 32 and etag or None
    if not browser_id:
      user_agent = self.persist_user_agent
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
      user_agent = user_agent or self.persist_user_agent
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

def exception_handler(exception, request, out):
  """To be passed into the fwerks module for general exception handling.

  We define the general exception handling function here for easy access to
  other tools in this module. This function is designed to be passed to the
  FWerks application constructor function in `request.py`.

  `exception` is the exception object that was caught.
  `request` is a Werkzeug request object.
  `out` is a callable used to create a Werkzeug response object.
  """
  logging.exception(exception)
  if ON_DEV_SERVER:
    response = out(utils.trace_out())
    response.status_code = 500
  else:
    # TODO: A nice 500 response.
    response = InternalServerError()
  return response

def not_found(response):
  """To be passed into the fwerks module to handle unmatched paths.

  We define the general 'not found' handler here for easy access to other tools
  in this module. This function is designed to be passed to the FWerks
  application constructor function in `request.py`.

  `response` A pre-constructed response object.
  """
  # TODO: A nice 404 response.
  response = set_default_headers(response)

  # We have to set all the headers using the header dictionary on the response
  # because the NotFound class does not have utility wrappers for them.
  response.headers['Expires'] = '-1'
  response.headers['Pragma'] = 'no-cache'
  response.headers['Cache-Control'] = NO_CACHE_HEADER
  response.headers['Content-Type'] = 'text/html; charset=utf-8'
  response.headers['Connection'] = 'close'
  return response

def request_redirect(response):
  """To be passed into the fwerks module to handle mis-matched paths.

  We define the general 'redirect' handler here for easy access to other tools
  in this module. This function is designed to be passed to the FWerks
  application constructor function in `request.py`.

  `response` A pre-constructed response object.
  """
  # There is no need to format a nice redirect response, since
  # browsers will automatically redirect
  response = set_default_headers(response)

  # Expire in 4 weeks.
  response.headers['Expires'] = http_date(time.time() + (86400 * 28))
  response.headers['Cache-Control'] = 'public, max-age=%d' % (86400 * 28)
  response.headers['Connection'] = 'close'
  return response

class SimpleHandler(BaseHandler):
  """General request handling class for most of the requests we get.

  This class is designed and written to be used by the fwerks module.  It
  handles typical GET and HEAD requests.

  Two objects are bound to all instances of this class by FWerks. The first,
  referenced by 'self.request' is a Werkzeug request object. The second,
  'self.out' is a callable object that will return a Werkzeug response object
  when invoked.

  Consult the Werkzeug reference documentation at
  http://werkzeug.pocoo.org/documentation/0.6.2/wrappers.html or in
  `werkzeug/wrappers.py` for more information about the request and response
  objects.
  """
  # Prepare and send the response.
  def respond(self):
    # Prepare the response.
    response = set_default_headers(
        self.out(
          utils.render_template(self.name)))
    response.mimetype = 'text/html'

    # Expire in 4 days.
    response.expires = int(time.time()) + (86400 * 4)

    return self.finalize_response(response)

  def get(self):
    """Accept the HTTP GET method."""
    return self.respond()

  def head(self):
    """Accept the HTTP HEAD method."""
    return self.respond()

class DatastoreHandler(BaseHandler):
  """Base class for datastore handlers.

  This class is designed and written to be used by the fwerks module.  It
  handles typical GET, PUT, and HEAD requests for the datastore URL space.

  Two objects are bound to all instances of this class by FWerks. The first,
  referenced by 'self.request' is a Werkzeug request object. The second,
  'self.out' is a callable object that will return a Werkzeug response object
  when invoked.

  Consult the Werkzeug reference documentation at
  http://werkzeug.pocoo.org/documentation/0.6.2/wrappers.html or in
  `werkzeug/wrappers.py` for more information about the request and response
  objects.
  """
  # Create a JSON response.
  def json_response(self, data=None):
    if data is None:
      response = self.out()
    else:
      response = self.out(simplejson.dumps(data))

    response.mimetype = 'application/json'
    return response

  # Create an HTML response.
  def html_response(self, template, context):
    if template is None:
      response = self.out()
    else:
      context['referrer'] = self.request.referrer
      response = self.out(utils.render_template(template, context))

    response.mimetype = 'text/html'
    return response

  # Prepare and send the response.
  def respond(self, status,
              data=None,
              template='datastore_generic',
              context={},
              record_request=True):

    if self.request.accept_mimetypes.best_match(
        ['application/json', 'text/html']) == 'application/json':
      response = set_default_headers(self.json_response(data))
    else:
      response = set_default_headers(self.html_response(template, context))

    response.status_code = status

    # No caching.
    response.headers['Expires'] = 'Fri, 01 Jan 1990 00:00:00 GMT'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Cache-Control'] = NO_CACHE_HEADER

    return self.finalize_response(response, record_request=record_request)

  def response_error(self, name, message):
    return {'name': name, 'message': message}

  def head(self):
    """Accept the HTTP HEAD method."""
    return self.respond(200)

  def get(self):
    """Accept the HTTP GET method."""
    # Querying is not yet implemented.
    return self.respond(200)

class DatastoreMembers(DatastoreHandler):
  """Handler for /datastore/members/ URL."""

  def post(self):
    """Accept the HTTP POST method.

    This method checks to see if a member with the same uid as was passed in
    with the POST data already exists, and if not, creates it.
    """
    data = self.request.form
    ack = data.get('acknowledgment')
    if not ack:
      message = 'Missing "acknowledgment" property.'
      e = self.response_error('ValidationError', message)
      return self.respond(409,
                          data=e,
                          template='datastore_error',
                          context={'message': message})

    name = data.get('name')
    if not name:
      message = 'Missing "name" property.'
      e = self.response_error('ValidationError', message)
      return self.respond(409,
                          data=e,
                          template='datastore_error',
                          context={'message': message})

    email = data.get('email')
    if not email:
      message = 'Missing "email" property.'
      e = self.response_error('ValidationError', message)
      return self.respond(409,
                          data=e,
                          template='datastore_error',
                          context={'message': message})

    # Check to see if a member with the same email address already exists.
    q = dstore.Member.all(keys_only=True)
    if q.filter('uid =', email).count(1):
      message = 'Member email already exists.'
      e = self.response_error('ConflictError', message)
      return self.respond(409,
                          data=e,
                          template='datastore_error',
                          context={'message': message})

    # Log this post and send a notification email.
    logging.info('New member posting: name=%s, email=%s', name, email)
    new_member = dstore.Member(member_name=name
                             , uid=email
                             , init_date=int(time.time()));
    if not self.no_persist:
      new_member.put()

    # TODO: The params for this email should not be hard coded in here.
    mail.send_mail(
        'kixxauth@gmail.com',
        'kixxauth@gmail.com',
        'New FWP member posted.',
        ('name: %s, email: %s' % (name, email)))

    json_data = {
          'member_name': new_member.member_name
        , 'uid'        : new_member.uid
        , 'init_date'  : new_member.init_date
        }

    return self.respond(201,
                        data=json_data,
                        template='datastore_members_post')

class DatastoreSubscribers(DatastoreHandler):
  """Handler for /datastore/subscribers/ URL."""

  def post(self):
    """Accept the HTTP POST method.

    If a subscriber with the provided email address already exists, the new
    subscription is added to the subscribers list if it is not already
    subscribed.  If a subscriber cannot be found with a matching email, a new
    subscriber is created before adding the subscription.
    """
    data = self.request.form
    email = data.get('email')
    new_sub = data.get('new_subscription')

    # Email is a required data field.
    if not email:
      message = 'Missing "email" property.'
      e = self.response_error('ValidationError', message)
      return self.respond(409,
                          data=e,
                          template='datastore_error',
                          context={'message': message})

    # Check for subscriber with the same email.
    q = dstore.Subscriber.all()
    subscriber = q.filter('email =', email).fetch(1)
    subscriber = len(subscriber) is 1 and subscriber[0] or None

    if subscriber:
      # Add new subscription.
      if new_sub and new_sub not in subscriber.subscriptions:
        subscriber.subscriptions.append(new_sub)
        if not self.no_persist:
          subscriber.put()

      json_data = {
              'email'        : subscriber.email
            , 'subscriptions': subscriber.subscriptions
            , 'init_date'    : subscriber.init_date
            }

      return self.respond(200,
                          data=json_data,
                          template='datastore_subscribers_post')

    # If a subscriber with the given email did not exist, create it.
    subs = new_sub and [new_sub] or []
    new_subscriber = dstore.Subscriber(email=email
                                     , subscriptions=subs
                                     , init_date=int(time.time()));
    if not self.no_persist:
      new_subscriber.put()

    json_data = {
          'email'        : new_subscriber.email
        , 'subscriptions': new_subscriber.subscriptions
        , 'init_date'    : new_subscriber.init_date
        }

    return self.respond(201,
                        data=json_data,
                        template='datastore_subscribers_post')

class DatastoreActions(DatastoreHandler):
  """Handler for /datastore/actions/ URL."""

  def post(self):
    """Accept the HTTP POST method.

    The request must send an attribute identifying the browser (not a browser
    session) which could be automatically generated in the datastore on the
    page request, or generated in client side code.  Either way, if a browser
    entity with the given key does not exist, we create it here and append the
    passed actions.
    """
    browser_id = self.request.cookies.get('bid') or 'anonymous'
    request_id = self.request.cookies.get('rid') or 'undefined'
    user_agent = self.persist_user_agent
    actions = map(lambda x: tuple(str(x).split(':'))
                , self.request.form.getlist('actions'))

    action_models = []
    logging.warn('actions: %r', self.request.form.getlist('actions'))
    try:
      for client_time, desc in actions:
        action_models.append(dstore.Action(browser=browser_id
                            , last_request=request_id
                            , user_agent=user_agent
                            , path=self.request.path
                            , address=self.request.remote_addr
                            , client_time=int(client_time)
                            , description=desc))
      if not self.no_persist:
        db.put(action_models)
    except ValueError, ex:
      logging.warn('Invalid "actions" property: %s', str(ex))
      message = 'Invalid "actions" property.'
      e = self.response_error('ValidationError', message)
      return self.respond(409,
                          data=e,
                          template='datastore_error',
                          context={'message': message})

    json_data = {
          'browser_id': browser_id
        , 'request_id': request_id
        , 'user_agent': user_agent
        , 'address': self.request.remote_addr
        , 'actions'   : map(lambda x: \
            {'client_time': x.client_time, 'description': x.description}
                          , action_models)
        }

    return self.respond(200, data=json_data, record_request=False)

class TestException(Handler):
  """Handler class for '/exception' URL.

  Designed to be used to test how the live server responds in the case of an
  exception.
  """
  def get(self):
    assert False, 'Test Exception Raised!'

# Create the handler map for export to the request handling script.  As you can
# see, the map is a list of tuples. The first item in each tuple is the URL
# rule for Werkzeug to match. The second item in each tuple is the name of the
# endpoint for Werkzeug. The third item in each tuple is a reference to the
# handler class for the fwerks module to use.
#
# Consult the Werkzeug rule formatting documentation for more info on
# constructing rules:
# http://werkzeug.pocoo.org/documentation/0.6.2/routing.html#rule-format
#
handler_map = [
      ('/', 'home', SimpleHandler)
    , ('/projects', 'projects', SimpleHandler)
    , ('/projects/', 'projects', SimpleHandler)
    , ('/join', 'join', SimpleHandler)
    , ('/about', 'about', SimpleHandler)
    , ('/datastore/members/', 'datastore_members', DatastoreMembers)
    , ('/datastore/subscribers/', 'datastore_subscribers', DatastoreSubscribers)
    , ('/datastore/actions/', 'datastore_actions', DatastoreActions)
    , ('/exception', 'exception', TestException)
    ]

