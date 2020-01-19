from django.contrib.auth import get_user_model

import rules
from rules import predicate


# BASIC ACCESS RULES
@predicate
def is_owner(user, obj):
    return obj.user == user


is_editor = rules.is_group_member('editors')
is_owner_or_editor = is_owner | is_editor


# PRIVACY RULES
def can_see(field: str):
    """
    A function that generates django-rules predicates when given a field name.

    For example, when called with 'description', it will generate a predicate that
    will contain the privacy checks for viewing the 'description' field.

    The generated predicate works like any other django-rules predicate, and can
    be used to construct rules.
    """
    name = f'can_see:{field}'

    @predicate(name)
    def fn(user: get_user_model(), obj):
        flag: bool = False
        if obj.user == user:

            flag = True
        return flag

    return fn


rules.add_perm('can_see_full_name', can_see('full_name') | is_owner | is_editor)
rules.add_perm('can_see_age', can_see('age') | is_owner | is_editor)
rules.add_perm('can_see_birthday', can_see('birthday') | is_owner | is_editor)
rules.add_perm('can_see_description', can_see('description') | is_owner | is_editor)
