{% extends "masthead-cols.tpl" %}

{% block styles %}
  <style type="text/css">
    {{ join_styles }}
  </style>
{% endblock styles %}

{% block content %}
      <div id="join-instructions">
        <h1>{{ join.header }}</h1>
        <p>
          {{ join.intro }}
        </p>
      </div>

      <div id="operating-agreement">
        {{ join.operating_agreement }}
      </div>

      <div id="join">
        <form action="" method="post" class="left-col"
              enctype="application/x-www-form-urlencoded">
          <p>
            <label for="name" accesskey="1">name:</label><input type="text" id="name" name="name" />
          </p>
          <p>
            <label for="email" accesskey="2">email:</label><input type="text" id="email" name="email" />
          </p>
          <p class="button-ctn">
            <input type="submit" class="button button-1" value="{{ join.button }}" />
          </p>
          <p class="content-text">
            {{ join.agreement }}
          </p>
        </form>
        <p class="right-col">
          {{ join.instructions }}
        </p>
      </div>
{% endblock content %}
