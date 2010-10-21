"""
    @file FWPWebsite.Google_App_Engine.dstore
    =========================================

    This module contains all the GAE datastore Model definitions as well is a
    few associated utility functions.

    @author Kris Walker <kixxauth@gmail.com>
    @copyright (c) 2010 by The Fireworks Project.
    @license MIT, see LICENSE for more details.
"""

from google.appengine.ext import db

class Member(db.Model):
  """The Member model definition.

  Instances of this class simply represent 'people' (presumably) that have
  signed the Fireworks Project Operating Agreement.
  """
  # ### The full name string of the member (first and last).
  member_name = db.StringProperty(required=True)

  # ### The unique identifier for this member.
  # This property is used to make sure that multiple memberships are not
  # created.  The email address of the member is a good value for this
  # property.
  uid = db.StringProperty(required=True)

  # ### The timestamp the member first subscribed.
  init_date = db.IntegerProperty()

class Subscriber(db.Model):
  """The Subscriber model definition.

  Subscriber instances are 'people' (presumably) that have signed up for email
  delivery of one of our subscription services like a blog feed or newsletter.
  """
  # ### The email address of the subscriber
  # This property is required for the subscription.
  email = db.StringProperty(required=True)

  # ### A list of subscriptions the subscriber is subscribed to.
  subscriptions = db.StringListProperty()

  # ### The timestamp the subscriber first subscribed.
  init_date = db.IntegerProperty()

class Browser(db.Model):
  """The Browser model definition.

  Browser instances represent a unique browser that has visited one of our
  pages. It is not a session ID, but a unique identifier associated with the
  user agent. We use a cookie to set the browser ID and ask the browser to
  identify itself on each subsequent request. Obviously user agents that do not
  persist cookies will be recorded as a new browser every time, and will need
  to be filtered.
  """
  # ### The time this entity was created on the server.
  # This property is automatically added when an instance is persisted.
  created = db.DateTimeProperty(auto_now_add=True)

  # ### The formatted user agent string.
  user_agent = db.StringProperty()

  # ### The first page that this browser visited.
  init_path = db.StringProperty()

  # ### The reffering URL that sent this browser here for the first time.
  init_referrer = db.StringProperty()

  # ### The IP address from which this browser came here for the first time.
  init_address = db.StringProperty()

def browser_key(browser):
  """Sanitize or extract a browser keyname for the datastore.

  @param {object|str} browser A Browser datastore instance or a keyname.
  @returns {str} The string repr of the key for the browsers.

  If a str is passed in, it is sanitized for use as a key in the GAE datastore.
  If an object is passed in, we assume it is a Browser instance and extract the
  unsanitized key string from it.
  """
  if isinstance(browser, basestring):
    return 'bid_'+ browser
  key = browser.key()
  key_name = key.name()
  return  key_name and key_name[4:] or str(key)

class Request(db.Model):
  """The Request model definition.

  A Request instance is created every time a client requests a page or
  (optionally) makes an API call.

  Because of client side caching, a request instance is not recorded on every
  page view; but if JS is active on the client, at least one Action instance
  will be recorded for each page view.
  """
  # ### The time this entity was created on the server.
  # This property is automatically added when an instance is persisted.
  created = db.DateTimeProperty(auto_now_add=True)

  # ### The given ID string for this browser.
  browser = db.StringProperty()

  # ### The formatted user agent string.
  user_agent = db.StringProperty()

  # ### The page requested.
  path = db.StringProperty()

  # ### The referring URL of the request.
  referrer = db.StringProperty()

  # ### The IP address of the client that made the request.
  address = db.StringProperty()

  # ### The HTTP status of the request.
  status = db.IntegerProperty()

class Action(db.Model):
  """The Action model definition.

  Instances of this model represent different actions a user may have taken on
  a page. These actions are recorded and sent here by Ajax JS running on the
  page.
  """
  # ### The time this entity was created on the server.
  # This property is automatically added when an instance is persisted.
  created = db.DateTimeProperty(auto_now_add=True)

  # ### The given ID string for this browser.
  browser = db.StringProperty()

  # ### The key string of the last request cookie sent by the server.
  last_request = db.StringProperty()

  # ### The formatted user agent string.
  user_agent = db.StringProperty()

  # ### The current path of the page view.
  path = db.StringProperty()

  # ### The IP address of the client.
  address = db.StringProperty()

  # ### The timestamp of the page load on the client.
  page_time = db.IntegerProperty()

  # ### The client side timestamp of the action.
  timestamp = db.IntegerProperty()

  # ### A description of the action.
  # The description could be anything the client wants to persist. The only
  # restriction is that it must be less than 500 chars.
  description = db.StringProperty()

