{% extends "masthead-cols.tpl" %}

{% block styles %}
  <style type="text/css">
    {{ join_styles }}
  </style>
{% endblock styles %}

{% block content %}
      <h1 id="join-header">{{ join.header }}</h1>

      <p id="join-instructions">
        {{ join.instructions }}
      </p>

      <div id="operating_agreement">
        {{ join.operating_agreement }}
      </div>

      <form id="join" action="" method="post"
            enctype="application/x-www-form-urlencoded">
        <p>
          <label for="name" accesskey="1">name:</label><input type="text" id="name" name="name" />
        </p>
        <p>
          <label for="email" accesskey="2">email:</label><input type="text" id="email" name="email" />
        </p>
        <p>
          <input type="submit" class="button_1" value="{{ join.button }}" />
        </p>
      </form>
{% endblock content %}
