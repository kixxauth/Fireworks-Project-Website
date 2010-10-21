* # 7.0 Improved WSGI implementation.

  * Improved code documentation and README.
  * Split up `handlers.py` into `base_handler.py`, `simple_handlers.py`, and
    `datastore_handlers.py`.
  * Moved HTTP Exception handlers to `exception_handlers.py`.
  * Moved URL mapping into `request.py`.
  * URL mapping now uses pure Werzeug utility.
  * `base_handler.py` includes definition of `Request` and `Response` classes.
  * HTTP Exception handlers now handle pure Werkzeug WSGI callables.
