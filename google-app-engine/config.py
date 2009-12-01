import os

# {dict} pages -> Mapping of handler names to page names.
# -------------------------------------------------------
# The pages dict needs to be maintained by hand to keep up to date with the
# request handlers in request.py and the stored page data in the datastore.
pages = {
    'home': ['home_1', 'The home page.'],
    'about': ['about_1', 'Content for information about the Fireworks Project.'],
    'projects_listing': ['projects_listing_1', 'The project listing page for public facing projects.'],
    'project-kixx': ['kixx_1', 'The project page for Kixx.'],
    'project-dcube': ['dcube_1', 'The project page for DCube.'],
    'project-crown_construction': ['crown_1', 'The home page for Crown Construction.'],
    'join': ['join_1', 'The sign up page.'],
    'not_found': ['not-found_1', 'Default 404 page.'],
    }

on_dev_server = os.environ['SERVER_SOFTWARE'].startswith('Development')
