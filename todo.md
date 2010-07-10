TODO:
=====

A prioritized todo list for The Fireworks Project website.
----------------------------------------------------------

### Before version 5 of the website can be moved to the live server:

#### Join page posting.

The join page has a form for new members to agree to the operating agreement.
We need to store the data for every user that submits this form and, for bonus
points, send an automated email to ourselves so we can contact the new member
ASAP. This was already handled in version 4 (the live site:
http://www.fireworksproject.com/join) but I'm proposing we do it a different
way.

I think we should provide a specific URL space for handling membership. An HTTP
GET request to `/members/` would return a list of all the members. An HTTP POST
request to `/members/` would create and store a new member entity and return
the generated id number. I think the `/members/` URL should only handle JSON
and the post form on `/join` should use AJAX to POST to `/members/`.  If the
browser is not using JavaScript then `/members/` will return some simple HTML
in response to the POST request.

---

#### E-Magazine subscriptions.

We need a handler to collect ezine subscription submissions from forms on the
website.

Ezine subscribers should also have its own URL space, just like the members.

---

### Join page styling.

The page at /join also needs to be styled.

---

### Projects page styling.

The page at /projects/ simply needs to be styled.

---

### About us page.

(Could we skip this a remove it from the navigation?)

The currently live version of the website has a /about page, but I have not
created one for version 5 yet. The handler needs to be created in
`/google-app-engine/request.py` and the template needs to be created in
`/google-app-engine/templates/`.

Also sombody should have a look at the content for this page and perhaps do
some editing.

---

### dcube, dcubejs, kixx, and kake pages.

(Could we skip this a remove it from the navigation?)

These pages should be the home pages for our active projects. Handlers for
`/projects/dcube`, `/projects/dcubejs`, `/projects/kixx`, and `projects/kake`
need to be created in request.py and the template needs to be created in
`/google-app-engine/templates/`.

The content for these pages can just be copied and pasted from the project
pages on GitHub http://github.com/FireworksProject

---

### Favicon.

Sombody needs to create a favicon. I have very little icon development knowledge, but
I'll learn it if nobody will.

---

### Site map.

Recreate the sitemap.xml file for search engines by hand. In a future version
we'll find a way to auto-generate this file.

---

### Fix flash of unstyled font.

There is an annoying flash of default typeface Typekit and Google Fonts load.


