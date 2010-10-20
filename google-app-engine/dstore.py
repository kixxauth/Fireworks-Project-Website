# TODO: Remove on production.
import logging

from google.appengine.ext import db

class Member(db.Model):
  member_name = db.StringProperty(required=True)
  uid = db.StringProperty(required=True)
  init_date = db.IntegerProperty()

class Subscriber(db.Model):
  email = db.StringProperty(required=True)
  subscriptions = db.StringListProperty()
  init_date = db.IntegerProperty()

class Browser(db.Model):
  created = db.DateTimeProperty(auto_now_add=True)
  user_agent = db.StringProperty()
  init_path = db.StringProperty()
  init_referrer = db.StringProperty()
  init_address = db.StringProperty()

def browser_key(browser):
  if isinstance(browser, basestring):
    return 'bid_'+ browser
  key = browser.key()
  key_name = key.name()
  return  key_name and key_name[4:] or str(key)

class Request(db.Model):
  created = db.DateTimeProperty(auto_now_add=True)
  browser = db.StringProperty()
  user_agent = db.StringProperty()
  path = db.StringProperty()
  referrer = db.StringProperty()
  address = db.StringProperty()
  status = db.IntegerProperty()

class Action(db.Model):
  created = db.DateTimeProperty(auto_now_add=True)
  browser = db.StringProperty()
  last_request = db.StringProperty()
  user_agent = db.StringProperty()
  path = db.StringProperty()
  address = db.StringProperty()
  page_time = db.IntegerProperty()
  timestamp = db.IntegerProperty()
  description = db.StringProperty()

