from django.db.models import Model

from rules.contrib.models import RulesModelBase, RulesModelMixin

from .. import rules


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
        # anyone who can edit a model, can see everything
        if user.has_perm(self.get_perm("change")):
            return True

        # default to false
        return False
