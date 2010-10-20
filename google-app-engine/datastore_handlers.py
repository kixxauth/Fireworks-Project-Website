import logging
import time

from google.appengine.ext import db
from google.appengine.api import mail
from django.utils import simplejson

import utils
import base_handler
import dstore

NO_CACHE_HEADER = utils.NO_CACHE_HEADER
render_template = utils.render_template

BaseHandler = base_handler.BaseHandler
Response    = base_handler.Response

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
      response = Response()
    else:
      response = Response(simplejson.dumps(data))

    response.mimetype = 'application/json'
    return response

  # Create an HTML response.
  def html_response(self, template, context):
    if template is None:
      response = Response()
    else:
      context['referrer'] = self.request.referrer
      response = Response(render_template(template, context))

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
      response = self.set_default_headers(self.json_response(data))
    else:
      response = self.set_default_headers(self.html_response(template, context))

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
    user_agent = self.user_agent_repr
    actions = map(lambda x: tuple(str(x).split(';'))
                , self.request.form.getlist('actions'))

    action_models = []
    try:
      for page_time, path, timestamp, desc in actions:
        action_models.append(dstore.Action(browser=browser_id
                            , last_request=request_id
                            , user_agent=user_agent
                            , path=path
                            , address=self.request.remote_addr
                            , page_time=int(page_time)
                            , timestamp=int(timestamp)
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

    def map_actions(x):
      return {
               'page_time': x.page_time
             , 'timestamp': x.timestamp
             , 'description': x.description
             }

    json_data = {
          'browser_id': browser_id
        , 'request_id': request_id
        , 'user_agent': user_agent
        , 'address': self.request.remote_addr
        , 'actions'   : map(map_actions, action_models)
        }

    return self.respond(200, data=json_data, record_request=False)

