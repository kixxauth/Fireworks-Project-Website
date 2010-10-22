TODO:
=====

A prioritized todo list for The Fireworks Project website.
----------------------------------------------------------

### Blockers for version 8:

#### OpenID integration (issue #6)
Luckily GAE has an OpenID implementation right out of the box:
http://code.google.com/appengine/articles/openid.html
http://blog.notdot.net/2010/05/Using-OpenID-authentication-on-App-Engine

We'll need to configure the handlers and possibly create a template to get this
working.

#### Expose the datastore to an HTTP API for Ajax (issue #9).
Our Collabworks apps, site anylitics app, and presumably our CMS are all going
to need some sort of HTTP API to expose the GAE datastore to client side JS.

#### Update testing framework (issue #1)
The crux of this issue is to get all these test categories to run and once and
print out to a dashboard. Therefore, I'm including Kake (our GUI build tool) as
a dependency for this issue.

Our testing framework is going to be implemented within the Kake build tool, so
we better get crackin' on that.

#### Execute a mobile strategy (issue #10).
This a multifaceted issue that will probably spawn a lot of dependency issues.
http://www.alistapart.com/articles/return-of-the-mobile-stylesheet

