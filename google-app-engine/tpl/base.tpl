<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <title>{{ subtitle }} - {{ title }}</title>
  <link rel="stylesheet" href="css/master.css">
</head>
<body>
  <div id="page">

    <div id="header">
      <h1 id="logo">
        <a href="/" title="Back to the home page.">
          The Fireworks Project
        </a>
      </h1>
      <h2 id="subheading">{{ subhead }}</h2>
    </div><!-- end #header -->

    <ul id="navigation">
      <li><a href="/" title="{{ nav.home.title }}">{{ nav.home.name }}</a></li>
      <li><a href="projects/" title="{{ nav.projects.title }}">{{ nav.projects.name }}</a></li>
      <li><a href="join" title="{{ nav.join.title }}">{{ nav.join.name }}</a></li>
      <li><a href="about" title="{{ nav.about.title }}">{{ nav.about.name }}</a></li>
    </ul><!-- end #navigation -->

    <div id="masthead">
      {% block masthead %}
      {% endblock masthead %}
    </div><!-- end #masthead -->

    <div id="content">
      {% block content %}
      {% endblock content %}
    </div><!-- end #content -->

  </div><!-- end #page -->

  <div id="footer">
    <div id="footer-wrapper">
    {{ footer }}
    </div><!-- end #footer-wrapper -->
  </div><!-- end #footer -->

</body>
</html>
