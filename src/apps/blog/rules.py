import rules
from rules import is_group_member, predicate


@predicate
def is_author(user, obj=None):
    if obj is None:
        return False
    author = getattr(obj, 'author', None)
    if author is None:
        return False
    # Post.author is an Author model (has .user); Comment.author is a User directly
    return getattr(author, 'user', author) == user


is_editor = is_group_member('moderators') | rules.is_staff
is_owner_or_editor = is_author | is_editor

rules.add_perm('blog.manage_posts', is_editor)
