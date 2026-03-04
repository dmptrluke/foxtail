import logging

from django.db.models import Model

from rules.contrib.models import RulesModelBase, RulesModelMixin

from .. import rules
from ..constants import PrivacyChoices

logger = logging.getLogger(__name__)


class BaseModel(RulesModelMixin, Model, metaclass=RulesModelBase):
    """
    Implements shared custom logic used by directory models.
    """

    class Meta:
        abstract = True

        rules_permissions = {
            'change': rules.is_owner_or_editor,
        }

    def can_view(self, field, user):
        # get the privacy field from the model
        rule = getattr(self, f'{field}_privacy', None)

        # make sure it actually exists, and is valid
        if rule is None:
            logger.error('Tried to call can_view with an invalid field "%s" on model "%s"',
                         field, self.__class__.__name__)
            return False

        if user.has_perm(self.get_perm("change")):
            # if you can edit the model, you can see everything
            return True

        if rule == PrivacyChoices.PUBLIC:
            return True
        elif rule == PrivacyChoices.SIGNED_IN:
            return user.is_authenticated
        else:
            return False
