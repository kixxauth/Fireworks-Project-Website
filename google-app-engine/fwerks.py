"""
    @file FWPWebsite.Google_App_Engine.fwerks
    =========================================
    FWerks is a quick and dirty framework for creating WSGI application callables
    using the Werkzeug utilities. The WSGI application constructor is built by
    the class `App` defined in this file. Check out the docs string for `App` to
    learn a lot more about how this process works.

    @author Kris Walker <kixxauth@gmail.com>
    @copyright (c) 2010 by The Fireworks Project.
    @license MIT, see LICENSE for more details.
"""

import logging

from werkzeug.exceptions import HTTPException, MethodNotAllowed, InternalServerError

class App(object):
    """Create a WSGI conforming callable application.
    -------------------------------------------------

    From PEP 333:
    The application object is simply a callable object that accepts two
    arguments. The term "object" should not be misconstrued as requiring an
    actual object instance: a function, method, class, or instance with a
    __call__    method are all acceptable for use as an application object.The
    application object must accept two positional arguments. For the sake of
    illustration, we have named them environ and start_response, but they are not
    required to have these names.

    In our case, to create the application the `App` constructor needs to be
    passed a url map, handler dictionary, and exception handler dictionary. The
    resulting `App` callable is designed to be passed to the Google App Engine
    `run_bare_wsgi_app()` function like this::

        from fwerks import App, Handler
        from google.appengine.ext.webapp.util import run_bare_wsgi_app

        class IndexHandler(Handler):
            def get(self):
                return werkzeug.Response('Hello World!')

        handler_map = [('/', 'index', IndexHandler)]
        my_awesome_app = App(handler_map)

        def main():
            run_bare_wsgi_app(my_awesome_app)

        if __name__ == "__main__":
            main()

    See [PEP 333](http://www.python.org/dev/peps/pep-0333/) for more info:

    As you can see we're using the Werkzeug utility framework to create the WSGI
    application:    http://werkzeug.pocoo.org/

    """
    def __init__(self, url_map, handlers, error_handlers={}):
        self.url_map = url_map
        self.handlers = handlers
        self.error_handlers = error_handlers

    def __call__(self, environ, start_response):
        try:
            # Construct a Werkzeug adapter object that is bound to the CGI
            # environment for this request.
            url_adapter = self.url_map.bind_to_environ(environ)

            # Dispatch the request to the correct handler and method.
            endpoint, matched_values = url_adapter.match()
            handler = self.handlers.get(endpoint)(endpoint, environ)
            response = handler(matched_values)

        # One particularly interesting thing about Werkzeug is that HTTPException
        # objects are WSGI conforming callable objects. So, if we can catch them,
        # we can use them to form the response.
        except HTTPException, e:
            error_handler = self.error_handlers.get(e.name, None)
            if error_handler and callable(error_handler):
                try:
                    response = error_handler(e, environ)
                except Exception, handlerex:
                    logging.warn('Caught exception in error handler %.', e.name)
                    logging.exception(handlerex)
                    response = e
            else:
                logging.debug('No exception handler for %s.', e.name)
                response = e

        except Exception, e:
            logging.warn('Caught unexpected exception.')
            logging.exception(e)
            error_handler = self.error_handlers.get('*', None)
            if error_handler and callable(error_handler):
                logging.debug('Calling error handler.')
                try:
                    response = error_handler(e, environ)
                except Exception, handlerex:
                    logging.warn('Caught exception in error handler.')
                    logging.exception(handlerex)
                    response = InternalServerError()
            else:
                logging.debug('Using default error handler.')
                response = InternalServerError()

        return response(environ, start_response)

class Handler(object):
    """Request handler base class.
    ------------------------------

    All request handlers should be subclasses of this class.    Handler subclasses
    should define any HTTP methods they wish to support by defining methods named
    'get', 'post', 'put', 'delete', 'head', or 'options'.

    Handler methods will be called when a request matching their path rule and
    method name arrives. Any parameters defined in the routing rule which was
    passed to `werkzeug.Rule()` will be passed to the handler method. See the
    [Werkzeug documentation on rule
    formatting](http://werkzeug.pocoo.org/documentation/0.6.2/routing.html#rule-format)
    to see how rules work.

    @property {string} name: The name of a Handler instance is simply the endpoint
    string which was set by the url map and was routed here by the dispatcher.
    @property {dict} environ: The CGI environment dictionary in case the instance
    needs access to it.

    """
    methods = ['get', 'post', 'put', 'delete', 'head', 'options']

    def __init__(self, endpoint, environ):
        self.name = endpoint
        self.environ = environ

    def __call__(self, arguments):
        method_handler = getattr(self, self.request.method.lower(), None)

        if callable(method_handler):
            return method_handler(**arguments)

        allowed = [m.upper() \
                for m in Handler.methods if getattr(self, m, None)]
        raise MethodNotAllowed(allowed)


class User(object):

    def __init__(self, session):
        pass


class AuthRequest(object):

    def __init__(self, federated_id):
        pass

