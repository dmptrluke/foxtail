from django.contrib.auth.models import Group

import pytest


@pytest.fixture
def editor(second_user):
    group, _ = Group.objects.get_or_create(name='Blog Editors')
    second_user.groups.add(group)
    second_user.save()
    return second_user


@pytest.fixture
def moderator(fourth_user):
    group, _ = Group.objects.get_or_create(name='Moderators')
    fourth_user.groups.add(group)
    fourth_user.save()
    return fourth_user
