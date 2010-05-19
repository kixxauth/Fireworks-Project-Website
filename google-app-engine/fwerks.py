
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, MethodNotAllowed
from werkzeug.exceptions import NotFound, InternalServerError
from werkzeug import BaseRequest, BaseResponse, CommonResponseDescriptorsMixin

class Response(BaseResponse, CommonResponseDescriptorsMixin):
    """Response class implementing the following Werkzeug mixins:

    - :class:`CommonResponseDescriptorsMixin` for various HTTP descriptors
    """

class App(object):
  """Create a WSGI conforming callable application.

  See PEP 333 for more info:
  http://www.python.org/dev/peps/pep-0333/

  From PEP 333:
  The application object is simply a callable object that accepts two
  arguments. The term "object" should not be misconstrued as requiring an
  actual object instance: a function, method, class, or instance with a
  __call__  method are all acceptable for use as an application object.The
  application object must accept two positional arguments. For the sake of
  illustration, we have named them environ and start_response, but they are not
  required to have these names.

  In our case, to create the application the `App` constructor needs to be
  passed a handler map. The resulting `App` callable is designed to be passed
  to the Google App Engine `run_bare_wsgi_app()` function like this::

    from fwerks import App, Handler
    from google.appengine.ext.webapp.util import run_bare_wsgi_app

    class IndexHandler(Handler):
      def get(self):
        return self.out('Hello World!')

    handler_map = [('/', 'index', IndexHandler)]
    my_awesome_app = App(handler_map)

    def main():
      run_bare_wsgi_app(my_awesome_app)

    if __name__ == "__main__":
      main()


  As you can see we're using the Werkzeug utility framework to create the WSGI
  application:  http://werkzeug.pocoo.org/

  """
  def __init__(self, mapping, exception_handler, not_found):
    self.handlers = {}
    self.exception_handler = exception_handler
    self.not_found = not_found

    def combiner(x):
      string, ep, handler_class = x
      self.handlers[ep] = handler_class
      return Rule(string, endpoint=ep)

    # Use a list comprehension and combiner function to create both the handler
    # dict and Werkzeug url_map list at the same time.
    self.url_map = Map([combiner(x) for x in mapping])

  def __call__(self, env, start_response):
    # Construct a Werkzeug request object.
    request = BaseRequest(env)

    # Construct a Werkzeug adapter object.
    url_adapter = self.url_map.bind_to_environ(env)

    # There are two Werkzeug exceptions we are particularly interested in
    # catching: `NotFound` and `RequestRedirect`. Both of which are
    # subclasses of HTTPException.  One particularly interesting thing about
    # Werkzeug is that these exception objects are callable and return a
    # value that can be passed back as WSGI app runner.
    try:
      # Dispatch the request to the correct handler and method.
      endpoint, arguments = url_adapter.match()
      handler_constructor = self.handlers.get(endpoint)
      handler = handler_constructor(request, Response)

      # If all goes well, the handler will return the callable response object
      # which we will return to the WSGI app runner that invoked us.
      response = handler(arguments)
    except NotFound, e:
      if callable(self.not_found):
        response = self.not_found(request, Response)
      else:
        response = e
    except HTTPException, e:
      response = e
    except Exception, e:
      if callable(self.exception_handler):
        response = self.exception_handler(e, request, Response)
      else:
        response = InternalServerError()
    return response(env, start_response)

class Handler(object):
  methods = ['get', 'post', 'put', 'delete', 'head', 'options']
  def __init__(self, request, response_constructor):
    self.request = request
    self.out = response_constructor

  def __call__(self, arguments):
    method_handler = getattr(self, self.request.method.lower(), None)

    if callable(method_handler):
      return method_handler(**arguments)

    allowed = [m for m in Handler.methods if getattr(self, m, None)]
    raise MethodNotAllowed(allowed)

