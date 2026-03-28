import json
from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.html import format_html


def dashboard_callback(request, context):
    from apps.accounts.models import User
    from apps.blog.models import Comment, Post
    from apps.content.models import Page
    from apps.events.models import Event
    from apps.organisations.models import Organisation

    now = timezone.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    # User stats
    total_users = User.objects.count()
    new_this_week = User.objects.filter(date_joined__gte=week_ago).count()
    new_this_month = User.objects.filter(date_joined__gte=month_ago).count()

    # Content counts
    total_events = Event.objects.count()
    total_orgs = Organisation.objects.count()
    total_posts = Post.objects.count()
    total_pages = Page.objects.count()

    # Registration chart (past 30 days)
    signups_by_day = (
        User.objects.filter(date_joined__gte=month_ago)
        .annotate(day=TruncDate('date_joined'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    signup_map = {row['day']: row['count'] for row in signups_by_day}
    chart_labels = []
    chart_data = []
    for i in range(30):
        day = (month_ago + timedelta(days=i)).date()
        chart_labels.append(date_format(day, 'M j'))
        chart_data.append(signup_map.get(day, 0))

    registration_chart = json.dumps(
        {
            'labels': chart_labels,
            'datasets': [
                {
                    'label': 'Signups',
                    'data': chart_data,
                    'borderColor': 'oklch(55.5% 0.115 280)',
                    'backgroundColor': 'oklch(55.5% 0.115 280 / 0.1)',
                    'fill': True,
                    'tension': 0.3,
                }
            ],
        }
    )

    # Recent blog posts
    recent_posts = Post.objects.select_related('author').order_by('-created')[:5]
    posts_table = {
        'headers': ['Title', 'Author', 'Created'],
        'rows': [
            {
                'cols': [
                    format_html(
                        '<a href="{}" class="text-primary-600 dark:text-primary-400">{}</a>',
                        reverse('admin:foxtail_blog_post_change', args=[p.pk]),
                        p.title,
                    ),
                    str(p.author) if p.author else '-',
                    date_format(p.created, 'M j, Y'),
                ],
            }
            for p in recent_posts
        ],
    }

    # Recent signups
    recent_users = User.objects.order_by('-date_joined')[:5]
    signups_table = {
        'headers': ['User', 'Email', 'Joined'],
        'rows': [
            {
                'cols': [
                    format_html(
                        '<a href="{}" class="text-primary-600 dark:text-primary-400">{}</a>',
                        reverse('admin:accounts_user_change', args=[u.pk]),
                        u.username,
                    ),
                    u.email,
                    date_format(u.date_joined, 'M j, Y'),
                ],
            }
            for u in recent_users
        ],
    }

    # Recent comments
    recent_comments = Comment.objects.select_related('post', 'author').order_by('-created')[:10]
    comments_table = {
        'headers': ['Comment', 'Post', 'Author', 'Approved', ''],
        'rows': [
            {
                'cols': [
                    c.text[:60] + ('...' if len(c.text) > 60 else ''),
                    format_html(
                        '<a href="{}" class="text-primary-600 dark:text-primary-400">{}</a>',
                        reverse('admin:foxtail_blog_post_change', args=[c.post_id]),
                        c.post.title[:30],
                    ),
                    str(c.author) if c.author else 'Anonymous',
                    format_html(
                        '<span class="inline-block font-semibold rounded-default text-[11px]'
                        ' uppercase whitespace-nowrap h-6 leading-6 px-2 {}">{}</span>',
                        'bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400'
                        if c.approved
                        else 'bg-orange-100 text-orange-700 dark:bg-orange-500/20 dark:text-orange-400',
                        'Yes' if c.approved else 'Pending',
                    ),
                    format_html(
                        '<a href="{}" class="text-primary-600 dark:text-primary-400 text-xs">Edit</a>',
                        reverse('admin:foxtail_blog_comment_change', args=[c.pk]),
                    ),
                ],
            }
            for c in recent_comments
        ],
    }

    # Upcoming events
    upcoming_events = Event.objects.filter(start__gte=now.date()).select_related('organisation').order_by('start')[:5]
    events_table = {
        'headers': ['Event', 'Organisation', 'Date'],
        'rows': [
            {
                'cols': [
                    format_html(
                        '<a href="{}" class="text-primary-600 dark:text-primary-400">{}</a>',
                        reverse('admin:events_event_change', args=[e.pk]),
                        e.title,
                    ),
                    str(e.organisation) if e.organisation else '-',
                    date_format(e.start, 'M j, Y'),
                ],
            }
            for e in upcoming_events
        ],
    }

    context.update(
        {
            'total_users': total_users,
            'new_this_week': new_this_week,
            'new_this_month': new_this_month,
            'total_events': total_events,
            'total_orgs': total_orgs,
            'total_posts': total_posts,
            'total_pages': total_pages,
            'registration_chart': registration_chart,
            'posts_table': posts_table,
            'signups_table': signups_table,
            'comments_table': comments_table,
            'events_table': events_table,
        }
    )

    return context
