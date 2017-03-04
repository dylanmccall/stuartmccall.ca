{% load json_tools %}{% spaceless %}
var SMC_GALLERIES = {{ galleries_dict|json_dumps|safe }};
{% endspaceless %}