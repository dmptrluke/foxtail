from django.contrib.auth.models import Group

import pytest


@pytest.fixture
def editor(second_user):
    group, _ = Group.objects.get_or_create(name='moderators')
    second_user.groups.add(group)
    second_user.save()
    return second_user


@pytest.fixture
def staff_user(second_user):
    second_user.is_staff = True
    second_user.save()
    return second_user
