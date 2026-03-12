import rules
from rules import is_group_member

is_editor = is_group_member('Event Editors') | rules.is_staff

rules.add_perm('events.manage_events', is_editor)
