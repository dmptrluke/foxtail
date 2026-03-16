from django.contrib.auth.models import Group

import pytest


@pytest.fixture
def editor(second_user):
    group, _ = Group.objects.get_or_create(name='Event Editors')
    second_user.groups.add(group)
    second_user.save()
    return second_user
