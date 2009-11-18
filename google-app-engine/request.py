# our config settings
import config

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

class IndexHandler(webapp.RequestHandler):
  def get(self):
    self.response.out.write('*The Fireworks Project Home Page*')

class AboutHandler(webapp.RequestHandler):
  def get(self):
    self.response.out.write('*About The Fireworks Project*')

class ProjectsListHandler(webapp.RequestHandler):
  def get(self):
    self.response.out.write("Look at all the cool projects we're working on")

class ProjectsHandler(webapp.RequestHandler):
  def get(self, project):
    self.response.out.write('This is the project page for %s'% project)

class JoinHandler(webapp.RequestHandler):
  def get(self, project):
    self.response.out.write('*Join Our Circus*')

class NotFoundHandler(webapp.RequestHandler):
  def get(self):
    self.response.out.write('! This page was not found.');

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

  # Not Found
  ('/.*', NotFoundHandler)
], debug=config.on_dev_server)

def main():
  util.run_wsgi_app(application)

if __name__ == "__main__":
  main()
