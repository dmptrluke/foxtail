from django.db import models


class AgeRequirement(models.TextChoices):
    """Define supported age requirements"""

    UNSPECIFIED = '', 'Unspecified'
    ALL = 'all', 'All Ages'
    THIRTEEN = '13', '13+'
    SIXTEEN = '16', '16+'
    EIGHTEEN = '18', '18+'
