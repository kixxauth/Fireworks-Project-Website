{% extends base.tpl %}

{% block masthead %}
      <div class="left-col">
        {{ masthead.left }}
      </div><!-- end .left-col -->
      <div class="right-col">
        <h1 class="pre-heading">{{ masthead.right.pre_heading }}</h1>
        <h1 class="heading">{{ masthead.right.heading }}</h1>
        {{ masthead.right.content }}
      </div><!-- end .right-col -->
{% endblock masthead %}

{% block content %}
      {{ content }}
{% endblock content %}
