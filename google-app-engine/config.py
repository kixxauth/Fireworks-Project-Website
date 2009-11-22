import os

# {dict} pages -> Mapping of handler names to page names.
# -------------------------------------------------------
# The pages dict needs to be maintained by hand to keep up to date with the
# request handlers in request.py and the stored page data in the datastore.
pages = {
    'home': 'home_1',
    'about': 'about_1',
    'projects_listing': 'projects_listing_1',
    'project-kixx': 'kixx_1',
    'project-dcube': 'dcube_1',
    'project-crown_construction': 'crown_1',
    'about': 'about_1',
    'not_found': 'not-found_1',
    }

on_dev_server = os.environ['SERVER_SOFTWARE'].startswith('Development')
