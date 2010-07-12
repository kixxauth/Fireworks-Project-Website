"""
  FWPWebsite.utils
  ~~~~~~~~~~~~~~~~
  Basic utilities toolkit.

  :copyright: (c) 2010 by The Fireworks Project.
  :license: MIT, see LICENSE for more details.
"""

import os
import sys
import cgi
import traceback
import hashlib

from google.appengine.ext.webapp import template

def get_template_path(name):
  """Return the full path of a template given its name.
  """
  # The current location is something like:
  # /base/data/home/apps/fireworkscomputer/4.341390069856818952/utils.py
  # So the os.path.dirname(__file__) is something like:
  # /base/data/home/apps/fireworkscomputer/4.341390069856818952/
  # And the template dir is something like:
  # /base/data/home/apps/fireworkscomputer/4.341390069856818952/templates/
  return os.path.join(os.path.dirname(__file__), 'templates', name)

def render_template(name, context=None):
  """Return a string rendered from a template.

  `name` The string name of the template to use.
  `context` The context data to inject into the template.

  ! Remember Django templates have an inheritence feature:
  http://docs.djangoproject.com/en/1.2/topics/templates/#id1
  """
  return template.render(get_template_path('%s.html'% name), context)

def trace_out():
  """Create and return a system trace string for debugging.
  """
  lines = ''.join(traceback.format_exception(*sys.exc_info()))
  return cgi.escape(lines, quote=True)

