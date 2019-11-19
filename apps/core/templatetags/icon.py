from django import template
from django.utils.html import format_html
from django.templatetags.static import static

register = template.Library()


@register.simple_tag(name='icon')
def icon_tag(icon):
    return format_html(
        "<div class='icon icon-{0} svg-baseline'><svg>"
        "<use xlink:href='{1}#icon-{0}'></use></svg></div>",
        icon,
        static('icons_r1.svg'),
    )
