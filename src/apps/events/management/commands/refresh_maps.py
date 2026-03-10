from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.events.maptiler import geocode
from apps.events.models import Event


class Command(BaseCommand):
    help = 'Re-geocode event addresses.'

    def add_arguments(self, parser):
        parser.add_argument('--event', type=int, help='Process a single event by ID')

    def handle(self, *args, **options):
        api_key = settings.MAPTILER_API_KEY
        if not api_key:
            raise CommandError('MAPTILER_API_KEY is not set.')

        events = Event.objects.all()
        if options['event']:
            events = events.filter(pk=options['event'])

        events = events.exclude(address='')
        total = events.count()
        self.stdout.write(f'Processing {total} event(s)...')

        geocoded = 0
        errors = 0

        for event in events:
            self.stdout.write(f'  {event.title}', ending='')

            coords = geocode(event.address, api_key)
            if coords:
                event.latitude, event.longitude = coords
                event.save(update_fields=['latitude', 'longitude'])
                geocoded += 1
                self.stdout.write(' [geocoded]')
            else:
                self.stdout.write(' [geocode failed]')
                errors += 1

        self.stdout.write(self.style.SUCCESS(f'Done: {geocoded} geocoded, {errors} errors.'))
