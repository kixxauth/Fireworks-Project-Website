import logging

import base_handler
import utils

BaseHandler = base_handler.BaseHandler
Response = base_handler.Response

class Entry(BaseHandler):
    """Entry point for the Crown Construction applications.
    """
    
    def get(self):
        """Accept the HTTP GET method."""
        user = self.user
        if user is None:
            response = self.federated_login_response('/crown_construction')
        else:
            response = Response(utils.render_template('crown_construction'))
            response.mimetype = 'text/html'

        return self.finalize_response(self.no_cache_response(response))

    def head(self):
        """Accept the HTTP HEAD method."""
        return self.get()

