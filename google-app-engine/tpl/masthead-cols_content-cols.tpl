{% extends "base.tpl" %}

{% block masthead %}
      <div class="left-col">
        {{ masthead.left }}
      </div><!-- end .left-col -->
      <div class="right-col">
        <h3 class="pre-heading">{{ masthead.right.pre_heading }}</h3>
        <h2 class="heading">{{ masthead.right.heading }}</h2>
        {{ masthead.right.content }}
      </div><!-- end .right-col -->
{% endblock masthead %}

{% block content %}
      <div class="left-col">
        {{ content.left }}
      </div><!-- end .left-col -->
      <div class="right-col">
        {{ content.right }}
      </div><!-- end .right-col -->
{% endblock content %}
