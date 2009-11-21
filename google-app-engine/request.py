# our config settings
import config

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from django.utils import simplejson

import os

class Page(db.Model):
  """This class serves as a model for datastore entities that represent a
  single page of this website.  Each page of the site has a Page model that
  encapsulates it.
  """
  # The output of template rendering.
  # Thie is the actual text/markup that will form the body of the response.
  rendered = db.TextProperty()

def sanitizePageName(name):
  """Entities of type Page are stored with a user supplied key, so we
  use this function to make sure the supplied key is valid.
  """
  return 'page:'+ name

def getPage(name):
  # will return null if the Page entity does not exist
  return Page.get_by_key_name(sanitizePageName(name))

def getRenderedPage(name):
  page = getPage(name)
  if page is None:
    return None
  return page.rendered

class IndexHandler(webapp.RequestHandler):
  def get(self):
    self.response.out.write(
        open(os.path.abspath(os.path.join('tpl', 'index.html'))).read())

class AboutHandler(webapp.RequestHandler):
  def get(self):
    page = getRenderedPage('about_1');
    if page is None:
      self.response.set_status(404)
      self.response.out.write('<h1>Todo: Create a better "not found" page.</h1>')

class ProjectsListHandler(webapp.RequestHandler):
  def get(self):
    page = getRenderedPage('projects_1');
    if page is None:
      self.response.set_status(404)
      self.response.out.write('<h1>Todo: Create a better "not found" page.</h1>')

class ProjectsHandler(webapp.RequestHandler):
  def get(self, project):
    page = getRenderedPage('project_1');
    if page is None:
      self.response.set_status(404)
      self.response.out.write('<h1>Todo: Create a better "not found" page.</h1>')

class JoinHandler(webapp.RequestHandler):
  def get(self):
    page = getRenderedPage('join_1');
    if page is None:
      self.response.set_status(404)
      self.response.out.write('<h1>Todo: Create a better "not found" page.</h1>')

class NotFoundHandler(webapp.RequestHandler):
  def get(self):
    self.response.out.write('! This page was not found.');

class TemplateListHandler(webapp.RequestHandler):
  #todo: protect with authentication
  def get(self):
    def readf(f):
      return {'name': f,
          'content': open(os.path.abspath(os.path.join('tpl', f))).read()}

    self.response.headers['Content-Type'] = 'text/plain'
    self.response.out.write(
        simplejson.dumps([readf(f) for f in os.listdir('tpl')]))

application = webapp.WSGIApplication([
  # Homepage
  # www.fireworksproject.com/
  ('/', IndexHandler),

  # About page
  # www.fireworksproject.com/about
  ('/about', AboutHandler),

  # Projects page
  # www.fireworksproject.com/projects
  ('/projects/?', ProjectsListHandler), 

  # Projects pages
  # www.fireworksproject.com/projects/(PROJECT_NAME)
  ('/projects/(\w+)', ProjectsHandler), 

  # Join page
  # www.fireworksproject.com/join
  ('/join', JoinHandler),

  # Admin: view available templates
  ('/content-manager/templates/', TemplateListHandler),

  # Not Found
  ('/.*', NotFoundHandler)
], debug=config.on_dev_server)

def main():
  util.run_wsgi_app(application)

if __name__ == "__main__":
  main()
