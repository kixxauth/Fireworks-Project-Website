# our config settings
import config

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from django.utils import simplejson
from google.appengine.ext.webapp import template
from google.appengine.api import mail

import logging

import os
import re

class Page(db.Model):
  """This class serves as a model for datastore entities that represent a
  single page of this website.  Each page of the site has a Page model that
  encapsulates it.
  """
  # The output of template rendering.
  # Thie is the actual text/markup that will form the body of the response.
  rendered = db.TextProperty(indexed=False)
  configs = db.TextProperty(indexed=False)

class ContentItem(db.Model):
  """This class serves as a model for datastore entities that represent a
  single content item in our content inventory. These items may be mixed and
  matched, and applied to templates to render the page output.
  """
  content = db.ListProperty(db.Text, required=True, indexed=False)
  description = db.StringProperty(indexed=False)

class NewMember(db.Model):
  """This class is a subclass of db.Model that is used to keep records of
  users who have posted their intention to join The Fireworks Project under
  the agreement on http://www.fireworksproject.com/join
  """
  name = db.StringProperty(required=True)
  email = db.StringProperty(required=True)

def sanitizePageName(name):
  """Entities of type Page are stored with a user supplied key, so we
  use this function to make sure the supplied key is valid.
  """
  return 'page:'+ name

def desanitizePageName(name):
  if not name:
    return name
  return name.replace('page:', '')

class BaseHandler(webapp.RequestHandler):
  def handleUnconfigured(self, msg):
    self.response.set_status(503)
    self.response.out.write('<h1>Todo: Create a better "error" page.</h1>')
    self.response.out.write('<p>'+ msg +'</p>')

  def getRenderedPage(self, name):
    page = Page.get_by_key_name(sanitizePageName(name))
    if page is None:
      return None
    return page.rendered

  def respond(self, page):
    self.response.out.write(page.rendered)

  def handleGet(self, name):
    configs = config.pages.get(name)
    if configs is None:
      self.handleNotFound()
      return

    page = Page.get_by_key_name(sanitizePageName(configs[0]))
    if page is None:
      self.handleUnconfigured('No page data found for %s'% configs[0])
      return

    self.respond(page)

  def handleNotFound(self):
    self.response.set_status(404)
    page_name = config.pages.get('not_found')[0]
    if page_name is None:
      self.response.out.write('<h1>Todo: Create a better "Not Found" page.</h1>')
      return

    page = Page.get_by_key_name(sanitizePageName(page_name))
    if page is None:
      self.response.out.write('<h1>Todo: Create a better "Not Found" page.</h1>')
      return

    self.response.out.write(page.rendered)

class IndexHandler(BaseHandler):
  def get(self):
    self.handleGet('home')

class AboutHandler(BaseHandler):
  def get(self):
    self.handleGet('about')

class ProjectsListHandler(BaseHandler):
  def get(self):
    self.handleGet('projects_listing')

class ProjectsHandler(BaseHandler):
  def get(self, project_name):
    self.handleGet('project-'+ project_name)

class JoinHandler(BaseHandler):
  def get(self):
    self.handleGet('join')

  def post(self):
    name = self.request.get('name', 'not-given')
    email = self.request.get('email', 'not-given')

    if name == 'automatedtest':
      return

    logging.info('New member posting to /join (name: %s, email: %s)',
        name, email)
    NewMember(name=name,email=email).put()
    mail.send_mail(
        config.join_notify_sender,
        config.join_notify_receiver,
        config.join_notify_subject,
        ('name: %s, email: %s' % (name, email)))
    self.handleGet('join-post')

class NotFoundHandler(BaseHandler):
  def get(self):
    self.handleNotFound()

class TemplateListHandler(webapp.RequestHandler):
  def get(self):
    #todo: protect with authentication
    def readf(f):
      return {'name': f,
          'content': open(os.path.abspath(os.path.join('tpl', f))).read()}

    self.response.headers['Content-Type'] = 'text/plain'
    self.response.out.write(
        simplejson.dumps([readf(f) for f in os.listdir('tpl') if f != 'README.txt']))

def readPage(page):
  if page is None:
    return page

  name = desanitizePageName(page.key().name())
  return {
      'name': name,
      'uri': 'http://%s/content-manager/pages/%s'% (os.environ.get('HTTP_HOST'), name),
      'configs': simplejson.loads(page.configs),
      'rendered': page.rendered
      }

class PageListHandler(webapp.RequestHandler):
  def get(self):
    #todo: protect with authentication
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.out.write(
        simplejson.dumps([readPage(p) for p in Page.all()]))

def constructDefaults(configs):
  rv = {}
  for n in configs:
    if isinstance(configs[n], dict):
      rv[n] = constructDefaults(configs[n])
      if rv[n] is False:
        return False
    else:
      try:
        content = ContentItem.get_by_id(configs[n]).content
      except:
        return False

      rv[n] = content[(len(content) -1)].decode('utf-8')

  return rv

def constructContext(configs):
  defaults = Page.get_by_key_name('defaults_1')
  if defaults is None:
    context = {}
  else:
    context = constructDefaults(simplejson.loads(defaults.configs))

  return constructContextRe(configs, context)

def constructContextRe(configs, context=None):
  def getItem(item):
    if isinstance(item, dict) or isinstance(item, list):
      return constructContextRe(item)
    else:
      try:
        content = ContentItem.get_by_id(item).content
      except:
        # todo: log this error
        return False

      return content[(len(content) -1)].decode('utf-8')

  if isinstance(configs, dict):
    if context is None:
      context = {}
    for k in configs:
      v = getItem(configs[k])
      if v is False:
        return v
      context[k] = v;

  else:
    if context is None:
      context = []
    for i in configs:
      v = getItem(i)
      if v is False:
        return v
      context.append(v);

  return context

class PageHandler(webapp.RequestHandler):
  def get(self, page_name):
    #todo: protect with authentication
    page = Page.get_by_key_name(sanitizePageName(page_name))
    if page is None:
      self.response.set_status(404)
      self.response.out.write('<h1>Todo: Create a better "not found" page.</h1>')
      return

    self.response.out.write(page.rendered)

  def put(self, page_name):
    #todo: protect with authentication
    self.response.headers['Content-Type'] = 'text/plain'

    if re.search('[^\w\-]+', page_name):
      self.response.set_status(400)
      self.response.out.write('unallowed characters in page name')
      return

    page = Page.get_by_key_name(sanitizePageName(page_name))
    if page is None:
      self.response.headers['Location'] = ('http://www.fireworksproject.com/'
        'content-manager/pages/%s'% page_name)
      self.response.set_status(201)
      page = Page(key_name=sanitizePageName(page_name))

    try:
      page_data = simplejson.loads(self.request.body)
    except:
      self.response.set_status(400)
      self.response.out.write('invalid JSON data: '+ self.request.body)
      return

    try:
      for snip in page_data:
        # snip[0] -> the template name
        # snip[1] -> the context object configuration
        context = constructContext(snip[1])
        if context is False:
          self.response.set_status(400)
          self.response.out.write('invalid context object: '+ simplejson.dumps(snip[1]))
          return

        page.rendered = template.render(
            os.path.join(os.path.dirname(__file__), 'tpl', snip[0]),
            context)
    except Exception, e:
      self.response.set_status(400)
      self.response.out.write(repr(e))
      return

    page.configs = self.request.body
    page.put()
    self.response.out.write(simplejson.dumps(readPage(page)))

def readContentItem(item):
  if item is None:
    return item
  return {
      'id': item.key().id(),
      'description': item.description,
      'content': item.content 
      }

class InventoryListHandler(webapp.RequestHandler):
  def get(self):
    #todo: protect with authentication
    self.response.headers['Content-Type'] = 'text/plain'
    #todo: as the content inventory gets large,
    # a wholesale data dump might not be a good idea
    self.response.out.write(
        simplejson.dumps([readContentItem(i) for i in ContentItem.all()]))

  def post(self):
    #todo: protect with authentication
    context = simplejson.loads(self.request.body)
    id = context.get('id')
    #todo: sanitize content ??
    content = db.Text(context.get('content'))
    desc = context.get('description')

    item = None

    if id:
      item = ContentItem.get_by_id(id)

      if item is None:
        self.response.set_status(400)
        self.response.out.write('id not found: %s'% id)
        return

      item.content.append(content)

    else:
      item = ContentItem(content=[content])

    item.description = desc
    item.put()
        
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.set_status(200)
    self.response.out.write(simplejson.dumps(readContentItem(item)))

class ConfigsHandler(webapp.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.out.write(simplejson.dumps(config.pages))

class DefaultsHandler(webapp.RequestHandler):
  def get(self):
    rv = '{}'

    defaults = Page.get_by_key_name('defaults_1')

    if defaults is not None:
      rv = defaults.configs

    self.response.headers['Content-Type'] = 'text/plain'
    self.response.out.write(rv)

  def put(self):
    self.response.headers['Content-Type'] = 'text/plain'

    defaults = Page.get_by_key_name('defaults_1')

    if defaults is None:
      self.response.headers['Location'] = ('http://www.fireworksproject.com/'
        'content-manager/defaults')
      self.response.set_status(201)
      defaults = Page(key_name='defaults_1')

    try:
      configs = simplejson.loads(self.request.body)
    except:
      self.response.set_status(400)
      self.response.out.write('invalid JSON: '+ self.request.body)
      return

    loaded = constructDefaults(configs)

    if loaded is False:
      self.response.set_status(400)
      self.response.out.write('invalid context object: '+ self.request.body)
      return

    defaults.configs = self.request.body
    defaults.put()
    self.response.out.write(defaults.configs)

class TestContentHandler(webapp.RequestHandler):
  def post(self):
    if not config.on_dev_server:
      self.response.set_status(403)
      return

    content = self.request.get('content')
    name = self.request.get('name')

    if not name:
      self.response.set_status(409)
      self.response.out.write('invalid post data "%s"' % self.request.body)
      return

    key_name = sanitizePageName(name)
    page = Page.get_by_key_name(key_name) or Page(key_name=key_name)
    page.rendered = content
    page.put()
    self.response.set_status(204)

class EnvironsHandler(webapp.RequestHandler):
  def get(self):
    for name in os.environ.keys():
      self.response.out.write("%s = %s<br />\n" % (name, os.environ[name]))

  def post(self):
    headers = self.request.headers
    r = '' 
    for header in headers:
      r += header +" = "+ headers[header] +"\n"
    b = self.request.body
    self.response.headers["Content-Type"] = "text/plain"
    self.response.out.write("\n << REQUEST HEADERS >>\n"+ r)
    self.response.out.write("\n << REQUEST BODY >>\n"+ b)

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

  # Admin: view page entities
  ('/content-manager/pages/', PageListHandler),

  # Admin: PUT or GET a page entity (PUT compiles templates)
  ('/content-manager/pages/(.*)', PageHandler),

  # Admin: view or POST content entities
  ('/content-manager/inventory/', InventoryListHandler),

  # Admin: GET configs
  ('/content-manager/configs', ConfigsHandler),

  # Admin: GET or PUT default content object
  ('/content-manager/defaults', DefaultsHandler),

  # Root: This url is used by the local dev_appserver ONLY
  # Loads CMS data into the local datastore for testing on dev_appserver.
  ('/testcontent/', TestContentHandler),

  # Admin: print out env variables
  ('/environs', EnvironsHandler),

  # Not Found
  ('/.*', NotFoundHandler)
], debug=config.on_dev_server)

def main():
  util.run_wsgi_app(application)

if __name__ == "__main__":
  main()
