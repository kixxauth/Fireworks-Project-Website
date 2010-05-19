import logging

from fwerks import App
from google.appengine.ext.webapp.util import run_bare_wsgi_app
from handlers import handler_map, exception_handler, not_found

fireworks_project_website = App(handler_map, exception_handler, not_found)

def main():
  run_bare_wsgi_app(fireworks_project_website)

if __name__ == "__main__":
  main()

