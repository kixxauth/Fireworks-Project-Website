<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <title>{% block title %}The Fireworks Project{% endblock %}</title>
  {% block style %}{% endblock %}
  {% block head %}{% endblock %}
</head>
<body>
<div id="page">
  <div id="header">
    <h1 id="logo"><a href="/">Fireworks Project</a></h1>
    <ul id="navigation">
      <li><a href="/">{{nav.home}}</a></li>
      <li><a href="/projects/">{{nav.projects}}</a></li>
      <li><a href="/join">{{nav.join}}</a></li>
      <li><a href="/about">{{nav.about}}</a></li>
    </ul>
  </div>

  {# <!-- Featured Content Slider --> #}
  <div id="masthead">
    {% block masthead %}{% endblock %}
  </div>

  {# <!-- Content --> #}
  <div id="content">
    {% block content %}{% endblock %}
  </div>

  {# <!-- Copyright, Site Map, Miscellaneous --> #}
  <div id="footer">
    {% block footer %}{% endblock %}
  </div>

</div><!-- page -->
</body>
</html>
