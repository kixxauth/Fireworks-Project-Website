Static
======

The static/ folder contains all the files and folders that will be served
statically from the App Engine servers rather than dynamically from python
scripts.  These files typically include CSS, Images, and downloads of various
kinds. None of these files are available to read or write to or from the
filesystem with Python scripts from the server.

Important files in this folder include:
---------------------------------------
* sitemap.xml : This is a data file for web crawlers. Currently we are maintaining it by hand.
* robots.txt : Served statically and maintained by hand.
* favicon.ico : Our favicon icon is served statically.
* googlef734612d306d87e6.html : Our Google web master tools ID
* y_key_36887132dd89194c.html : Our Yahoo! web master tools ID

Copyright and License
---------------------
copyright: (c) 2009 - 2010 by Fireworks Technology Projects Inc.

Unless otherwise indicated, all source code is licensed under the MIT license.
See MIT-LICENSE for details.

And, unless otherwise indicated, all content, including written copy and images
but not including source code, is licensed under a Creative Commons
Attribution-ShareAlike 3.0 Unported license. All derivatives of this content
must be attributed to
["The Fireworks Project"](http://www.fireworksproject.com/). See
[creativecommons.org/licenses/by-sa/3.0/](http://creativecommons.org/licenses/by-sa/3.0/)
for more details.

