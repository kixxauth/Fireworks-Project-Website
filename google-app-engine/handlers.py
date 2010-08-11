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
from werkzeug.exceptions import InternalServerError
from werkzeug.utils import http_date

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

  `request` is a Werkzeug request object.
  `out` is a callable used to create a Werkzeug response object.
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
  # There is no need to format a nice redirect response, since
  # browsers will automatically redirect
  response = set_default_headers(response)

  # Expire in 4 weeks.
  response.headers['Expires'] = http_date(time.time() + (86400 * 28))
  response.headers['Cache-Control'] = 'public, max-age=%d' % (86400 * 28)
  response.headers['Connection'] = 'close'
  return response

class SimpleHandler(Handler):
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
  # Default template name.
  template = 'home'

  # Prepare and send the response.
  def respond(self):
    set_cookie = False
    now = time.time()
    cache_control = 'public'
    browser = None
    key_name = None
    bid = self.request.cookies.get('bid')

    if bid:
      try:
        # In most cases the browser_id is a datastore key.
        browser = db.get(db.Key(encoded=bid))
      except db.BadKeyError:
        # But, sometimes it may be a key_name instead.
        key_name = 'bid_'+ bid
        browser = dstore.Browser.get_by_key_name(key_name)

    if browser is None:
      # Create a new browser object if it does not exist.
      set_cookie = True
      user_agent, user_agent_str = utils.format_user_agent(self.request)
      user_agent_str = (user_agent.browser and
                        user_agent_str or user_agent.string)
      browser = dstore.Browser(user_agent=user_agent_str)

    # Add this request to the list of requests made by this browser.
    req = dstore.format_request(int(now),
                                self.request.path,
                                self.request.remote_addr)
    browser.requests.append(req)
    k = str(browser.put())

    # Prepare the response.
    response = set_default_headers(
        self.out(
          utils.render_template(self.template)))
    response.mimetype = 'text/html'
    response.add_etag()

    if set_cookie:
      # Cookie expires in 1 year.
      response.set_cookie('bid',
                          value=(key_name and key_name[3:] or k),
                          expires=(now + 31556926))
      # No public caching when a cookie is sent.
      cache_control = 'private'

    # Expire in 4 days.
    response.expires = now + (86400 * 4)
    response.headers['Cache-Control'] = \
        '%s, max-age=%d' % (cache_control, (86400 * 4))

    return response.make_conditional(self.request)

  def get(self):
    """Accept the HTTP GET method."""
    return self.respond()

  def head(self):
    """Accept the HTTP HEAD method."""
    return self.respond()

class IndexHandler(SimpleHandler):
  """Handler class for '/' URL."""
  template = 'home'

class JoinHandler(SimpleHandler):
  """Handler class for '/join' URL."""
  template = 'join'

class ProjectsHandler(SimpleHandler):
  """Handler class for '/projects' URL."""
  template = 'projects'

class AboutHandler(SimpleHandler):
  """Handler class for '/about' URL."""
  template = 'about'

class DatastoreHandler(Handler):
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
  templates = {
      'post': 'datastore_default'
    , 'get' : 'datastore_default'
    , 'err' : 'datastore_default'
    }

  # Prepare and send the response.
  def respond(self, status, data=None):
    if self.request.accept_mimetypes.best_match(
        ['application/json', 'text/html']) == 'application/json':
      if data is None:
        response = self.out()
      else:
        response = self.out(simplejson.dumps(data))
      response.mimetype = 'application/json'
    else:
      if data is None:
        response = self.out()
      else:
        if status > 299:
          tpl = self.templates['err']
          context = {
              'message': data['name'] +': '+ data['message']
            , 'referrer': self.request.referrer
            }
        else:
          context = {'referrer': self.request.referrer}
          tpl = self.templates[self.request.method.lower()]
        response = self.out(utils.render_template(tpl, context))
      response.mimetype = 'text/html'

    response = set_default_headers(response)
    response.status_code = status
    response.add_etag()

    # No caching.
    response.headers['Expires'] = '-1'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Cache-Control'] = NO_CACHE_HEADER

    return response.make_conditional(self.request)

  def response_error(self, name, message):
    return {'name': name, 'message': message}

  def head(self):
    """Accept the HTTP HEAD method."""
    return self.respond(200, None)

class DatastoreMembers(DatastoreHandler):
  """Handler for /datastore/members/ URL."""

  templates = {
      'post': 'datastore_members_post'
    , 'get' : 'datastore_default'
    , 'err' : 'datastore_members_err'
    }

  def get(self):
    """Accept the HTTP GET method."""
    # Querying the member list is not yet implemented.
    return self.respond(200, {})

  def post(self):
    """Accept the HTTP POST method.

    This method checks to see if a member with the same uid as was passed in
    with the POST data already exists, and if not, creates it.
    """
    data = self.request.form
    ack = data.get('acknowledgment')
    if not ack:
      e = self.response_error('ValidationError', 'missing "acknowlegement" property')
      return self.respond(409, e)
    name = data.get('name')
    if not name:
      e = self.response_error('ValidationError', 'missing "name" property')
      return self.respond(409, e)
    email = data.get('email')
    if not email:
      e = self.response_error('ValidationError', 'missing "email" property')
      return self.respond(409, e)

    q = dstore.Member.all(keys_only=True)
    if q.filter('uid =', email).count(1):
      e = self.response_error('ConflictError', 'member already exists')
      return self.respond(409, e)

    logging.info('New member posting: name=%s, email=%s', name, email)
    new_member = dstore.Member(member_name=name
                             , uid=email
                             , init_date=int(time.time()));
    new_member.put()

    # TODO: The params for this email should not be hard coded in here.
    mail.send_mail(
        'kixxauth@gmail.com',
        'kixxauth@gmail.com',
        'New FWP member posted.',
        ('name: %s, email: %s' % (name, email)))

    return self.respond(201, {
          'member_name': new_member.member_name
        , 'uid'        : new_member.uid
        , 'init_date'  : new_member.init_date
        })

class DatastoreSubscribers(DatastoreHandler):
  """Handler for /datastore/subscribers/ URL."""

  templates = {
      'post': 'datastore_subscribers_post'
    , 'get' : 'datastore_default'
    , 'err' : 'datastore_subscribers_err'
    }

  def get(self):
    """Accept the HTTP GET method."""
    # Querying the subscriber list is not yet implemented.
    return self.respond(200, {})

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
      e = self.response_error('ValidationError', 'missing "email" property')
      return self.respond(409, e)

    # Check for subscriber with the same email.
    q = dstore.Subscriber.all()
    subscriber = q.filter('email =', email).fetch(1)
    subscriber = len(subscriber) is 1 and subscriber[0] or None
    if subscriber:

      # Add new subscription.
      if new_sub and new_sub not in subscriber.subscriptions:
        subscriber.subscriptions.append(new_sub)
        subscriber.put()

      return self.respond(200, {
            'email'        : subscriber.email
          , 'subscriptions': subscriber.subscriptions
          , 'init_date'    : subscriber.init_date
          })

    # If a subscriber with the given email did not exist, create it.
    subs = new_sub and [new_sub] or []
    new_subscriber = dstore.Subscriber(email=email
                                     , subscriptions=subs
                                     , init_date=int(time.time()));
    new_subscriber.put()
    return self.respond(201, {
          'email'        : new_subscriber.email
        , 'subscriptions': new_subscriber.subscriptions
        , 'init_date'    : new_subscriber.init_date
        })

class DatastoreActions(DatastoreHandler):
  """Handler for /datastore/actions/ URL."""

  def get(self):
    """Accept the HTTP GET method."""
    # Querying the subscriber list is not yet implemented.
    return self.respond(200, {})

  def post(self):
    """Accept the HTTP POST method.

    The request must send an attribute identifying the browser (not a browser
    session) which could be automatically generated in the datastore on the
    page request, or generated in client side code.  Either way, if a browser
    entity with the given key does not exist, we create it here and append the
    passed actions.
    """
    data = self.request.form

    browser_id = data.get('browser_id')
    if not browser_id:
      e = self.response_error('ValidationError', 'missing "browser_id" property')
      return self.respond(409, e)

    actions = data.get('actions')
    actions = isinstance(actions, list) and actions or [actions]

    key_name = None
    try:
      # In most cases the browser_id is a datastore key.
      browser = db.get(db.Key(encoded=browser_id))
    except db.BadKeyError:
      # But, sometimes it may be a key_name instead.
      key_name = 'bid_'+ browser_id
      browser = dstore.Browser.get_by_key_name(key_name)

    # If the browser entity does not exist, create it.
    if not browser:
      user_agent, user_agent_str = utils.format_user_agent(self.request)
      user_agent_str = (user_agent.browser and
                        user_agent_str or user_agent.string)
      if key_name:
        browser = dstore.Browser(key_name=key_name, user_agent=user_agent_str)
      else:
        browser = dstore.Browser(user_agent=user_agent_str)

    # Append the actions and persist the entity.
    browser.actions = browser.actions + actions
    k = str(browser.put())

    return self.respond(200, {
          'browser_id': key_name and key_name[3:] or k
        , 'user_agent': browser.user_agent
        , 'actions'   : len(browser.actions or [])
        , 'requests'  : len(browser.requests or [])
        })

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
      ('/', 'index', IndexHandler)
    , ('/projects', 'projects', ProjectsHandler)
    , ('/projects/', 'projects', ProjectsHandler)
    , ('/join', 'join', JoinHandler)
    , ('/about', 'about', AboutHandler)
    , ('/datastore/members/', 'datastore_members', DatastoreMembers)
    , ('/datastore/subscribers/', 'datastore_subscribers', DatastoreSubscribers)
    , ('/datastore/actions/', 'datastore_actions', DatastoreActions)
    , ('/exception', 'exception', TestException)
    ]

