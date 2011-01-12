Fireworks Project Website
=========================

This is the source code repository for the
[www.fireworksproject.com](http://www.fireworksproject.com) website.
It is hosted on the [Google App Engine platform in the Python runtime](http://code.google.com/appengine/docs/python/overview.html).

For more information, check out the [project wiki](http://github.com/FireworksProject/www.fireworksproject.com/wiki)

Quickstart for hackers and hitchhikers:
---------------------------------------

#### 1. Make sure you have Python installed on your computer.

Keep in mind that the App Engine environment runs python 2.5.2 and you might want to run the same version. [code.google.com/appengine/docs/python/runtime.html#Pure_Python](http://code.google.com/appengine/docs/python/runtime.html#Pure_Python)

#### 2. Download and install the App Engine SDK.

For Python: (Linux, Mac, and Windows) [code.google.com/appengine/downloads.html](http://code.google.com/appengine/downloads.html)

#### 3. Get the source code.

You can do this 1 of 2 ways. The best way is to use Git and create a GitHub
user account if you don't have one already. Fork the repository into your
GitHub account by clicking the 'Fork' button at
[github.com/FireworksProject/www.fireworksproject.com](http://github.com/FireworksProject/www.fireworksproject.com).
Then, clone the repository from GitHub on your local machine with

  `git clone http://github.com/USERNAME/www.fireworksproject.com.git`

where USERNAME is your GitHub username. Make sure to do this while you are in
the directory you wish to clone the repo to.
GitHub has [great instructions](http://help.github.com/forking/)
on how to complete the forking operation.

The second best way to get the source code is to download the latest package
from
[github.com/FireworksProject/www.fireworksproject.com/downloads](http://github.com/FireworksProject/www.fireworksproject.com/downloads).
Then unpack it in a local directory on your machine.

### 4. Run it.

To fire up the local development server from the SDK, you need to point it at
the application configuration file like this:

  `google_appengine/dev_appserver.py www.fireworksproject.com/google-app-engine/`

The dev\_appserver will look for `app.yaml` in
`www.fireworksproject.com/google-app-engine/`. For more information about
running the App Engine dev\_appserver consult the GAE docs
[code.google.com/appengine/docs/python/tools/devserver.html](http://code.google.com/appengine/docs/python/tools/devserver.html)

### 5. Have a look.

Once the dev_appserver is running you can __switch over to your browser__ to
see how things look. Just point your browser to
[http://localhost:8080/](http://localhost:8080/) and you should be off and
running.

### 6. Start hacking.

The best way to start is by actually reading through [the wiki](http://github.com/FireworksProject/www.fireworksproject.com/wiki) and then read the documentation
in `google-app-engine/README.md`.

__If you have any questions please contact me, the project manager, at kixxauth@gmail.com__

Copyright and License
---------------------
copyright: (c) 2009 - 2011 by Fireworks Technology Projects Inc.

Unless otherwise indicated, all source code is licensed under the MIT license.
See MIT-LICENSE for details.

And, unless otherwise indicated, all content, including written copy and images
but not including source code, is licensed under a Creative Commons
Attribution-ShareAlike 3.0 Unported license. All derivatives of this content
must be attributed to
["The Fireworks Project"](http://www.fireworksproject.com/). See
[creativecommons.org/licenses/by-sa/3.0/](http://creativecommons.org/licenses/by-sa/3.0/)
for more details.

