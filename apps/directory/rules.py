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
def can_view(model: str, field: str):
    """
    A function that generates django-rules predicates when given a field name.

    For example, when called with 'description', it will generate a predicate that
    will contain the privacy checks for viewing the 'description' field.

    The generated predicate works like any other django-rules predicate, and can
    be used to construct rules.
    """
    name = f'can_view:{model}:{field}'

    @predicate(name)
    def fn(user: get_user_model(), obj):
        flag: bool = False
        if obj.user == user:

            flag = True
        return flag

    return fn


rules.add_perm('view_profile_full_name', can_view('profile', 'full_name') | is_owner_or_editor)
rules.add_perm('view_profile_age', can_view('profile', 'age') | is_owner_or_editor)
rules.add_perm('view_profile_birthday', can_view('profile', 'birthday') | is_owner_or_editor)
rules.add_perm('view_profile_description', can_view('profile', 'description') | is_owner_or_editor)
