from django.apps import apps
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.db import models


class Command(BaseCommand):
    help = 'Clear image fields that reference missing files in storage.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='List missing images without clearing them.')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        total = 0

        for model in apps.get_models():
            image_fields = [f.name for f in model._meta.get_fields() if isinstance(f, models.ImageField)]
            if not image_fields:
                continue

            for field_name in image_fields:
                qs = model.objects.exclude(**{field_name: ''}).values_list('pk', field_name)
                for pk, path in qs:
                    if not default_storage.exists(path):
                        label = f'{model._meta.label} pk={pk} {path}'
                        if dry_run:
                            self.stdout.write(f'Missing: {label}')
                        else:
                            model.objects.filter(pk=pk).update(**{field_name: ''})
                            self.stdout.write(f'Cleared: {label}')
                        total += 1

        if total == 0:
            self.stdout.write(self.style.SUCCESS('No missing images found.'))
        elif dry_run:
            self.stdout.write(f'\n{total} missing image(s) found. Run without --dry-run to clear them.')
        else:
            self.stdout.write(self.style.SUCCESS(f'\nCleared {total} missing image(s).'))
