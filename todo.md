TODO:
=====

A prioritized todo list for The Fireworks Project website.
----------------------------------------------------------

### Blockers for version 8:

#### Incorporate a build tool (issue 2)
Port the project over to use Kake (our GUI builder) as the build and
deployment tool.

#### Update testing framework (issue 1)
The crux of this issue is to get all test categories to run and once and print
out to a dashboard. Therefore, Kake (our GUI build tool) is a dependency for
this issue.

#### Wrap the App Engine datastore API (issue 13)
This involves wrappers to make authorization and permissions on datatypes
explicit.

#### Expose the datastore to an HTTP API for Ajax (issue 9).
Our Collabworks apps, site anylitics app, and presumably our CMS are all going
to need some sort of HTTP API to expose the GAE datastore to client side JS.

#### Execute a mobile strategy (issue 10).
This a multifaceted issue that will probably spawn a lot of dependency issues.
http://www.alistapart.com/articles/return-of-the-mobile-stylesheet

