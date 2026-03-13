import rules
from rules import is_group_member

is_event_editor = rules.is_staff | is_group_member('Event Editors')

rules.add_perm('organisations.manage_organisations', is_event_editor)
rules.add_perm('organisations.manage_event_series', is_event_editor)
