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
  user_agent = db.StringProperty()
  requests = db.StringListProperty(indexed=False)
  actions = db.StringListProperty(indexed=False)

def format_request(timestamp, path, address, referrer):
  return '%d;%s;%s;%s'% (timestamp, path, address, referrer)

