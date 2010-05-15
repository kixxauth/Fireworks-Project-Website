"""This module contains the models and utility functions for working with the
App Engine datastore.
"""
import logging

from google.appengine.ext import db
from google.appengine.api import datastore
from google.appengine.api import datastore_errors

class BaseUser(db.Model):
  """Derived datastore model class for user managment."""
  __prefix = 'BaseUser:'
  passkey = db.StringProperty(indexed=False)
  nonce = db.StringProperty(indexed=False)
  nextnonce = db.StringProperty(indexed=False)
  groups = db.StringListProperty(default=['users'])

  def __init__(self, username=None, _from_entity=False, **kwds):
    if username is not None:
      # If the username is given, we assume that the constructor has been
      # called from the handler routine and we create this model with the
      # correct "sanitized" key_name.
      assert _from_entity is False
      self.username = username
      db.Model.__init__(self, key_name=self.__prefix + str(username))
    else:
      # If the username is not given, we assume this constructor was called
      # from the GAE datastore code, and construct the object like expected.
      assert _from_entity
      db.Model.__init__(self, _from_entity=True, **kwds)

  def __repr__(self):
    return '{username:%s, passkey:%s, nonce:%s, nextnonce:%s, groups:%s}'% \
        (self.username, self.passkey, self.nonce, self.nextnonce, self.groups)

  @classmethod
  def get(cls, name):
    """Allows a caller to get an instance of this class using only the name."""
    try:
      entity = datastore.Get(datastore.Key.from_path(
          cls.__name__, cls.__prefix + str(name)))
    except datastore_errors.EntityNotFoundError:
      return None
    user = cls.from_entity(entity)
    user.username = name
    return user

  def put(self):
    """Redirect db.Model.put() through our own put_user().

    This trick allows us to do better sanity checks.
    
    """
    put_user(self)

  @property
  def credentials(self):
    return [self.username, self.nonce, self.nextnonce]

def put_user(user):
  """Adds aditional sanity checks when saving a user entity to the datastore.

  """
  assert isinstance(user, BaseUser)
  assert isinstance(user.nonce, basestring)
  assert isinstance(user.nextnonce, basestring)
  db.put(user)

class Page(db.Model):
  """This class serves as a model for datastore entities that represent a
  single page of this website.  Each page of the site has a Page model that
  encapsulates it.
  """
  path = db.StringProperty(required=True)
  version = db.IntegerProperty(required=True)
  identities = db.StringListProperty(indexed=False)
  contents = db.ListProperty(db.Text, indexed=False)

