from django.core.management.base import BaseCommand

from apps.accounts.tests.factories import UserFactory
from apps.blog.tests.factories import CommentFactory, PostFactory
from apps.content.tests.factories import PageFactory
from apps.events.tests.factories import EventFactory


class Command(BaseCommand):
    help = 'Populate the database with sample data for development.'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=10, help='Number of users to create (default: 10)')
        parser.add_argument('--posts', type=int, default=20, help='Number of blog posts to create (default: 20)')
        parser.add_argument('--comments', type=int, default=30, help='Number of comments to create (default: 30)')
        parser.add_argument('--events', type=int, default=10, help='Number of events to create (default: 10)')
        parser.add_argument('--pages', type=int, default=5, help='Number of content pages to create (default: 5)')

    def handle(self, *args, **options):
        self.stdout.write('Generating sample data...')

        users_count = options['users']
        self.stdout.write(f'  Creating {users_count} users...')
        users = UserFactory.create_batch(users_count)
        self.stdout.write(self.style.SUCCESS(f'  Created {len(users)} users'))

        posts_count = options['posts']
        self.stdout.write(f'  Creating {posts_count} blog posts...')
        posts = PostFactory.create_batch(posts_count)
        self.stdout.write(self.style.SUCCESS(f'  Created {len(posts)} blog posts'))

        comments_count = options['comments']
        self.stdout.write(f'  Creating {comments_count} blog comments...')
        comments = CommentFactory.create_batch(comments_count)
        self.stdout.write(self.style.SUCCESS(f'  Created {len(comments)} comments'))

        events_count = options['events']
        self.stdout.write(f'  Creating {events_count} events...')
        events = EventFactory.create_batch(events_count)
        self.stdout.write(self.style.SUCCESS(f'  Created {len(events)} events'))

        pages_count = options['pages']
        self.stdout.write(f'  Creating {pages_count} content pages...')
        pages = PageFactory.create_batch(pages_count)
        self.stdout.write(self.style.SUCCESS(f'  Created {len(pages)} pages'))

        self.stdout.write(self.style.SUCCESS('\nSample data generation complete!'))
