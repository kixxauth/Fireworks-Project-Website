{% extends "masthead-cols.tpl" %}

{% block styles %}
  <style type="text/css">
{{ project_list_styles }}
  </style>
{% endblock styles %}

{% block content %}
  <h1>{{ projects_header }}</h1>
  {% for project in project_list %}
  <div class="project-button">
    <h3><a  href="{{ project.location }}">{{ project.name }}</a></h3>
    <p><a  href="{{ project.location }}">{{ project.description }}</a></p>
  </div>
  {% endfor %}
{% endblock content %}
