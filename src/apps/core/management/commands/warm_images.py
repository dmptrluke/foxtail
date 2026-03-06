from django.core.management.base import BaseCommand

from versatileimagefield.image_warmer import VersatileImageFieldWarmer

from apps.blog.models import Post
from apps.events.models import Event


class Command(BaseCommand):
    help = 'Regenerate all VersatileImageField renditions for posts and events.'

    def handle(self, *args, **options):
        posts = Post.objects.exclude(image='')
        if posts.exists():
            warmer = VersatileImageFieldWarmer(
                instance_or_queryset=posts, rendition_key_set='post_image', image_attr='image'
            )
            num, failed = warmer.warm()
            self.stdout.write(f'Post images: {num} renditions generated, {len(failed)} failed')
        else:
            self.stdout.write('No posts with images found')

        events = Event.objects.exclude(image='')
        if events.exists():
            warmer = VersatileImageFieldWarmer(
                instance_or_queryset=events, rendition_key_set='event_image', image_attr='image'
            )
            num, failed = warmer.warm()
            self.stdout.write(f'Event images: {num} renditions generated, {len(failed)} failed')
        else:
            self.stdout.write('No events with images found')

        self.stdout.write(self.style.SUCCESS('Done'))
