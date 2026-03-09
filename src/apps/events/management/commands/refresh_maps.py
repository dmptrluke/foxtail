from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError

from apps.events.mapbox import geocode, map_filename, static_map
from apps.events.models import Event


class Command(BaseCommand):
    help = 'Regenerate geocodes and map images for events.'

    def add_arguments(self, parser):
        parser.add_argument('--geocode', action='store_true', help='Re-geocode addresses (default: maps only)')
        parser.add_argument('--event', type=int, help='Process a single event by ID')

    def handle(self, *args, **options):
        token = settings.MAPBOX_ACCESS_TOKEN
        if not token:
            raise CommandError('MAPBOX_ACCESS_TOKEN is not set.')

        events = Event.objects.all()
        if options['event']:
            events = events.filter(pk=options['event'])

        events = events.exclude(address='')
        total = events.count()
        self.stdout.write(f'Processing {total} event(s)...')

        geocoded = 0
        mapped = 0
        errors = 0

        for event in events:
            self.stdout.write(f'  {event.title}', ending='')

            if options['geocode']:
                coords = geocode(event.address, token)
                if coords:
                    event.latitude, event.longitude = coords
                    geocoded += 1
                    self.stdout.write(' [geocoded]', ending='')
                else:
                    self.stdout.write(' [geocode failed]')
                    errors += 1
                    continue

            if event.latitude is None or event.longitude is None:
                self.stdout.write(' [no coordinates, skipping]')
                continue

            map_bytes = static_map(event.latitude, event.longitude, token)
            if map_bytes:
                filename = map_filename(event.address)
                if event.map_image:
                    event.map_image.delete(save=False)
                event.map_image.save(filename, ContentFile(map_bytes), save=False)
                mapped += 1
                self.stdout.write(' [map saved]')
            else:
                self.stdout.write(' [map failed]')
                errors += 1

            event.save(update_fields=['latitude', 'longitude', 'map_image'])

        self.stdout.write(self.style.SUCCESS(f'Done: {geocoded} geocoded, {mapped} maps generated, {errors} errors.'))
