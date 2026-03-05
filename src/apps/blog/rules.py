from rules import is_group_member, predicate


# BASIC ACCESS RULES
@predicate
def is_author(user, obj=None):
    if obj:
        return obj.author == user
    else:
        return False


is_moderator = is_group_member('moderators')
is_editor = is_group_member('editors')

is_owner_or_moderator = is_author | is_editor | is_moderator
is_owner_or_editor = is_author | is_editor
