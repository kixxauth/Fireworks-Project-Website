* # 8.0

  * OpenID endpoint discovery has been implemented with Python OpenID library.
  * Authentication session management added with the Beaker library.

* # 7.2

  * Disabled JS webfont loading and removed slideshow to fix rendering bug
    on mobile browsers.

* # 7.1

  * Fix collabworks priority dashboard popup issue in IE8.
  * Changed Python indent from 2 to 4 spaces.
  * Upadate copyright and license notifications.
  * Updated README files across the board.

* # 7.0 Improved WSGI implementation.

  * Improved code documentation and README.
  * Split up `handlers.py` into `base_handler.py`, `simple_handlers.py`, and
    `datastore_handlers.py`.
  * Moved HTTP Exception handlers to `exception_handlers.py`.
  * Moved URL mapping into `request.py`.
  * URL mapping now uses pure Werkzeug utility.
  * `base_handler.py` includes definition of `Request` and `Response` classes.
  * HTTP Exception handlers now handle pure Werkzeug WSGI callables.



