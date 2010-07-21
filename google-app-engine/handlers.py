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
from django.utils import simplejson

from fwerks import Handler
import utils
from werkzeug.exceptions import InternalServerError
from werkzeug.utils import http_date

import dstore

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

  # Default template context object.
  context = {
      'taglines': [
        'For big ideas.',
        'Dream big.',
        'Dream different.',
        'Simply more productive.',
        'Simply uncomplicated.',
        'Sheer simplicity.']
      }

  # Prepare and send the response.
  def respond(self):
    response = set_default_headers(
        self.out(
          utils.render_template(self.template, self.context)))
    response.mimetype = 'text/html'
    response.add_etag()

    # Expire in 4 days.
    response.expires = time.time() + (86400 * 4)
    response.headers['Cache-Control'] = 'public, max-age=%d' % (86400 * 4)

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

  # Prepare and send the response.
  def respond(self, status, data=None):
    if data is None:
      response = self.out()
    else:
      response = self.out(simplejson.dumps(data))

    response.status_code = status
    response = set_default_headers(response)
    response.mimetype = 'application/json'
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
    name = data.get('name')
    if not name:
      e = self.response_error('ValidationError', 'missing "name" property')
      return self.respond(400, e)
    email = data.get('email')
    if not email:
      e = self.response_error('ValidationError', 'missing "email" property')
      return self.respond(400, e)

    q = dstore.Member.all(keys_only=True)
    if q.filter('uid =', email).count(1):
      e = self.response_error('ConflictError', 'member exists')
      return self.respond(409, e)

    new_member = dstore.Member(member_name=name
                             , uid=email
                             , init_date=int(time.time()));
    new_member.put()
    return self.respond(201, {
          'member_name': new_member.member_name
        , 'uid'        : new_member.uid
        , 'init_date'  : new_member.init_date
        })

class DatastoreSubscribers(DatastoreHandler):
  """Handler for /datastore/members/ URL."""

  def get(self):
    """Accept the HTTP GET method."""
    # Querying the subscriber list is not yet implemented.
    return self.respond(200, {})

  def post(self):
    """Accept the HTTP POST method.

    """
    data = self.request.form
    email = data.get('email')
    new_sub = data.get('new_subscription')
    if not email:
      e = self.response_error('ValidationError', 'missing "email" property')
      return self.respond(400, e)

    q = dstore.Subscriber.all()
    subscriber = q.filter('email =', email).fetch(1)
    subscriber = len(subscriber) is 1 and subscriber[0] or None
    if subscriber:
      if new_sub and new_sub not in subscriber.subscriptions:
        subscriber.subscriptions.append(new_sub)
        subscriber.put()

      return self.respond(200, {
            'email'        : subscriber.email
          , 'subscriptions': subscriber.subscriptions
          , 'init_date'    : subscriber.init_date
          })

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
    , ('/datastore/members/', 'datastore_members', DatastoreMembers)
    , ('/datastore/subscribers/', 'datastore_subscribers', DatastoreSubscribers)
    , ('/exception', 'exception', TestException)
    ]

