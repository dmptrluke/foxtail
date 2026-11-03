from django.db import models


class ColorScheme(models.TextChoices):
    """Define supported color palettes"""

    PLUM = 'plum', 'Plum'
    SLATE = 'slate', 'Slate'
    COFFEE = 'coffee', 'Coffee'
    FOREST = 'forest', 'Forest'
    AUTUMN = 'autumn', 'Autumn'
    BERRY = 'berry', 'Berry'
    TUI = 'tui', 'Tui'
    TWILIGHT = 'twilight', 'Twilight'
    DUSK = 'dusk', 'Dusk'
    OCEAN = 'ocean', 'Ocean'
    CONTRAST = 'contrast', 'Contrast'


class AgeRequirement(models.TextChoices):
    """Define supported age requirements"""

    UNSPECIFIED = '', 'Unspecified'
    ALL = 'all', 'All Ages'
    THIRTEEN = '13', '13+'
    SIXTEEN = '16', '16+'
    EIGHTEEN = '18', '18+'
