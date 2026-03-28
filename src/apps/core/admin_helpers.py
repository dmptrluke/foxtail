from django.utils import timezone
from django.utils.html import escape
from django.utils.safestring import mark_safe

_BADGE_CLASSES = {
    'danger': 'bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400',
    'success': 'bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400',
    'info': 'bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-400',
}

_BADGE_TEMPLATE = (
    '<span class="inline-block font-semibold rounded-default text-[11px]'
    ' uppercase whitespace-nowrap h-6 leading-6 px-2 {classes}">{text}</span>'
)


def _badge(text, variant):
    return mark_safe(  # noqa: S308
        _BADGE_TEMPLATE.format(classes=_BADGE_CLASSES[variant], text=escape(text))
    )


def publish_status_badge(obj):
    """Return an unfold-styled badge for a django-published model's current status."""
    if obj.publish_status == 1:  # Available
        return _badge('Available', 'success')
    if obj.publish_status == 0:  # Never Available
        return _badge('Never Available', 'danger')
    # Available after date
    if obj.live_as_of is None:
        return _badge('No publish date set', 'info')
    if obj.live_as_of > timezone.now():
        return _badge(f'Available after {obj.live_as_of:%x}', 'info')
    return _badge('Available', 'success')
