"""
  FWPWebsite.request
  ~~~~~~~~~~~~~~~~~~
  WSGI application bootstrap for FWerks handlers.
  (see handlers.py for more info)

  When a request comes in to the GAE servers, and is routed to this script for
  handling, GAE calls the `main()` funtion. After the initial call is made, the
  entire app is cached to speed up future requests.

  Keeping the parsed Python code in memory saves time and allows for faster
  responses. Caching the global environment has other potential uses as well:

    Compiled regular expressions. All regular expressions are parsed and
    stored in a compiled form. You can store compiled regular expressions in
    global variables, then use app caching to re-use the compiled objects
    between requests.

    GqlQuery objects. The GQL query string is parsed when the GqlQuery object
    is created. Re-using a GqlQuery object with parameter binding and the
    bind() method is faster than re-constructing the object each time. You
    can store a GqlQuery object with parameter binding for the values in a
    global variable, then re-use it by binding new parameter values for each
    request.

    Configuration and data files. If your application loads and parses
    configuration data from a file, it can retain the parsed data in memory
    to avoid having to re-load the file with each request.

  !Important: Be careful to not "leak" user-specific information between
  requests. Avoid global variables unless caching is desired, and always
  initialize request-specific data inside the main() routine.

  Have a look at the Google Documentation for more information.
  http://code.google.com/appengine/docs/python/runtime.html

  Google App Engine gives us a sandboxed CGI environment
  (http://code.google.com/appengine/docs/python/runtime.html) to do our work
  in. We could just interact with CGI directly, (http://www.w3.org/CGI/) but it
  is much easier and more portable to use Python's WSGI specification
  (http://www.python.org/dev/peps/pep-0333/). You can learn more about WSGI at
  http://wsgi.org/wsgi/Learn_WSGI

  In our case, we've created a quick and dirty WSGI applicaton constructor from
  the WSGI utility collection called Werkzeug (http://werkzeug.pocoo.org/).
  We import our WSGI constructor, called `App` from the fwerks `fwerks.py` module.

  In the handlers `handlers.py` module we have a mapping object called
  `handler_map` that we pass to `App()` to create our WSGI application called
  `fireworks_project_website`. We also import the `exceptions_handler` and
  'not_found` handler functions from the handlers module and pass them to
  `App()` as well.

  App Engine provides us with a utility function to run our WSGI application
  called `run_bare_wsgi_app()` (oddly enough). We import that function from
  `google.appengine.ext.webapp.util` and invoke it in `main()` at the bottom
  of this script.

  :copyright: (c) 2010 by The Fireworks Project.
  :license: MIT, see LICENSE for more details.
"""

from fwerks import App
from google.appengine.ext.webapp.util import run_bare_wsgi_app
from handlers import handler_map, exception_handler, not_found, request_redirect
from werkzeug import BaseRequest, CommonRequestDescriptorsMixin, BaseResponse, AcceptMixin, CommonResponseDescriptorsMixin, ETagResponseMixin, ETagRequestMixin

class Request(BaseRequest, CommonRequestDescriptorsMixin, AcceptMixin, ETagRequestMixin):
  """Request class implementing the following Werkzeug mixins:

      - :class:`CommonRequestDescriptorsMixin` for various HTTP descriptors.
      - :class:`AcceptMixin` for the HTTP Accept header.
  """

class Response(BaseResponse, CommonResponseDescriptorsMixin, ETagResponseMixin):
  """Response class implementing the following Werkzeug mixins:

      - :class:`CommonResponseDescriptorsMixin` for various HTTP descriptors.
      - :class:`ETagResponseMixin` ETag and conditional response utilities.
  """

# Create a fwerks WSGI application object. Fwerks is our quick and dirty WSGI
# framework built with Werkzeug.
fireworks_project_website = App(handler_map, Request, Response
                              , exception_handler=exception_handler
                              , not_found=not_found
                              , request_redirect=request_redirect)

def main():
  """Called by App Engine for incoming requests.

  Since this handler script defines a function named main(), then the script and
  its global environment will be cached like an imported module. The first
  request for the script on a given web server evaluates the script normally.
  For subsequent requests, App Engine calls the main() function in the cached
  environment.
  """
  # Use GAE helper function to run the WSGI app.
  run_bare_wsgi_app(fireworks_project_website)

if __name__ == "__main__":
  main()

