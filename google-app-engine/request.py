"""
    @file FWPWebsite.Google_App_Engine.request
    ==========================================
    WSGI application bootstrap for FWerks handlers.
    (see FWPWebsite.Google_App_Engine.py for more info)

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
    We import our WSGI constructor, called `App` from the `fwerks.py` module.

    In this script we have a mapping object called `url_map` along with a
    matching `handlers` dictionary that we pass to `App()` to create our WSGI
    application called `fireworks_project_website`.

    App Engine provides us with a utility function to run our WSGI application
    called `run_bare_wsgi_app()` (oddly enough). We import that function from
    `google.appengine.ext.webapp.util` and invoke it in `main()` at the bottom
    of this script.

    @author Kris Walker <kixxauth@gmail.com>
    @copyright (c) 2010 by The Fireworks Project.
    @license MIT, see MIT-LICENSE for more details.
"""

from google.appengine.ext.webapp.util import run_bare_wsgi_app
from beaker.middleware import SessionMiddleware
from werkzeug.routing import Map, Rule, RequestRedirect

from fwerks import App
import base_handler
import simple_handlers
import datastore_handlers
import exception_handlers

beaker_session_configs = base_handler.beaker_session_configs
AuthRequestHandler     = base_handler.AuthRequestHandler
SimpleHandler          = simple_handlers.SimpleHandler
TestException          = simple_handlers.TestException
ShowEnvirons           = simple_handlers.ShowEnvirons
DatastoreMembers       = datastore_handlers.DatastoreMembers
DatastoreActions       = datastore_handlers.DatastoreActions
DatastoreSubscribers   = datastore_handlers.DatastoreSubscribers
not_found              = exception_handlers.not_found
request_redirect       = exception_handlers.request_redirect
exception_handler      = exception_handlers.exception_handler

# ### The handler map for export to the request handling script.
# As you can see, the url map is a Werkzeug Map object made up of a list of
# Werkzeug Rule objects. The first parameter to each Rule is the URL rule for
# Werkzeug to match. The second parameter is the name of the endpoint for
# Werkzeug.
#
# Consult the Werkzeug rule formatting documentation for more info on
# constructing rules:
# http://werkzeug.pocoo.org/documentation/0.6.2/routing.html#rule-format
url_map = Map([
          Rule('/', endpoint='home')
        , Rule('/projects', endpoint='projects')
        , Rule('/projects/', endpoint='projects')
        , Rule('/join', endpoint='join')
        , Rule('/about', endpoint='about')
        , Rule('/datastore/members/', endpoint='datastore_members')
        , Rule('/datastore/subscribers/', endpoint='datastore_subscribers')
        , Rule('/datastore/actions/', endpoint='datastore_actions')
        , Rule('/auth_request', endpoint='auth_request')
        , Rule('/cgi-env', endpoint='environs')
        , Rule('/exception', endpoint='exception')
        ])

# ### Request handlers.
# The WSGI application matches the `url_map` endpoints with these handler
# classes.  When a url with the corresponding endpoint is called, the handler
# class matching the endpoint is invoked and the newly created handler instance
# is returned to the WSGI handler.
handlers = {
          'home': SimpleHandler
        , 'projects': SimpleHandler
        , 'join': SimpleHandler
        , 'about': SimpleHandler
        , 'datastore_members': DatastoreMembers
        , 'datastore_subscribers': DatastoreSubscribers
        , 'datastore_actions': DatastoreActions
        , 'auth_request': AuthRequestHandler
        , 'environs': ShowEnvirons
        , 'exception': TestException
        }


# ### Exception handlers work a little differently.
# Whenever an HTTP exception is thrown by a handler, the exception handler
# registered to the string name of the HTTP error. If a handler cannot be
# found, the '*' handler is called.  Exception handlers are expected to take a
# Werkzeug HTTP exception object and the environment dictionary and return a
# WSGI application (callable object).
exception_handlers = {
          'Not Found': not_found
        , 'Moved Permanently': request_redirect
        , '*': exception_handler
        }


# ### Create a fwerks WSGI application object.
# Fwerks is our quick and dirty WSGI framework built with Werkzeug utilities.
# Check out the docs for [FWPWebsite.Google_App_Engine.fwerks.py] to learn all
# about it.
wsgi_app = App(url_map, handlers, exception_handlers)

# ### Add WSGI middleware for session management.
# We're using the Beaker module for user session management.
# Find out more at http://beaker.groovie.org/
wsgi_app = SessionMiddleware(wsgi_app, config=beaker_session_configs)


def main():
    """Called by App Engine for incoming requests.

    Since this handler script defines a function named main(), then the script and
    its global environment will be cached like an imported module. The first
    request for the script on a given web server evaluates the script normally.
    For subsequent requests, App Engine calls the main() function in the cached
    environment.
    """
    # Use GAE helper function to run the WSGI app.
    run_bare_wsgi_app(wsgi_app)

if __name__ == "__main__":
    main()

