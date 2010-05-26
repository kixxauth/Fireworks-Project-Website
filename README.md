Fireworks Project Website
=========================

This is the source code repository for the [www.fireworksproject.com][1] website.
It is hosted on the [Google App Engine platform in the Python runtime][2].

Quickstart for hackers and explorers:
-------------------------------------

1. __Make sure you have Python installed on your computer.__ Keep in mind that the
  App Engine environment runs python 2.5.2 and you might want to run the same
  version.  [code.google.com/appengine/docs/python/runtime.html#Pure_Python][3]

2. __Download and install the App Engine SDK__ for Python (Linux, Mac, and Windows)
[code.google.com/appengine/downloads.html][4]

3. __Get the source code__. You can do this 1 of 2 ways. The best way is to
  learn how to use Git and create a GitHub user account if you have don't have
  one already. Fork the repository into your GitHub account by clicking the
  'Fork' button at
  [github.com/FireworksProject/Fireworks-Project-Website](http://github.com/FireworksProject/Fireworks-Project-Website).
  Then, clone the repository from GitHub on your local machine with

    `git clone http://github.com/USERNAME/Fireworks-Project-Website.git`

  where USERNAME is your GitHub username. Make sure to do
  this while you are in the directory you wish to clone the repo to.

  The second best way to get the source code is to download the latest package
  from
  [github.com/FireworksProject/Fireworks-Project-Website/downloads](http://github.com/FireworksProject/Fireworks-Project-Website/downloads).
  Then unpack it in a local directory on your machine.

4. OK, now that you've got the source code you can actually __run it__. To fire
  up the local development server from the SDK, you need to point it at the
  application configuration file like this:

    `google_appengine/dev_appserver.py Fireworks-Project-Website/google-app-engine/`

  The dev_appserver will look for `app.yaml` in
  `Fireworks-Project-Website/google-app-engine/`. For more information about
  running the App Engine dev_appserver consult the GAE docs
  [code.google.com/appengine/docs/python/tools/devserver.html][5]

5. Once the dev_appserver is running you can __switch over to your browser__ to see
  how things look. Just point your browser to
  [http://localhost:8080/](http://localhost:8080/) and you should be off and
  running.

6. __Start hacking.__ The best way to start is by actually reading
`google-app-engine/README.md`.

If you have any questions please contact me, the project manager, at kixxauth@gmail.com


License
-------
Licensed under The MIT License:

The MIT License

Copyright (c) 2009 Fireworks Technology Projects Inc.
[www.fireworksproject.com][1]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

  [1]: http://www.fireworksproject.com
  [2]: http://code.google.com/appengine/docs/python/overview.html
  [3]: http://code.google.com/appengine/docs/python/runtime.html#Pure_Python
  [4]: http://code.google.com/appengine/downloads.html
  [5]: http://code.google.com/appengine/docs/python/tools/devserver.html

