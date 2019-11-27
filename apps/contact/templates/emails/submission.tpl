{% extends "mail_templated_simple/base.tpl" %}

{% block subject %}Contact form submission - {{ name }}{% endblock %}

{% block body %}
    A user has submitted a request using the contact form on the website. The details are below:

    Name: {{ name }}
    {% if authentication %}
        Authentication: {{ authentication }}
    {% endif %}
    Email: {{ email }}
    Message:
    {{ message }}
{% endblock %}
