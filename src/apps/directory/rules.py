import rules
from rules import predicate


# BASIC ACCESS RULES
@predicate
def is_owner(user, obj=None):
    if obj:
        return obj.user == user
    else:
        return False


is_editor = rules.is_group_member('editors')
is_owner_or_editor = is_owner | is_editor
