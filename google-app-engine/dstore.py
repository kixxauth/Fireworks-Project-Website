from google.appengine.ext import db

class Member(db.Model):
  member_name = db.StringProperty(required=True)
  uid = db.StringProperty(required=True)
  init_date = db.IntegerProperty()

