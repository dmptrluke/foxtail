from django.core.exceptions import ValidationError

import pytest

from apps.accounts.validators import validate_blacklist


def _blocked(username):
    with pytest.raises(ValidationError):
        validate_blacklist(username)


def _allowed(username):
    validate_blacklist(username)


class TestReservedWordBlocking:
    # exact reserved word is blocked
    def test_exact_match(self):
        _blocked('admin')

    # leet-speak substitution is caught
    @pytest.mark.parametrize('name', ['4dm1n', '@dmin', 'adm!n', '$taff'])
    def test_leet_speak(self, name):
        _blocked(name)

    # separator insertion is caught
    def test_separator_bypass(self):
        _blocked('a.d.m.i.n')

    # character repetition is caught
    @pytest.mark.parametrize('name', ['admiiiin', 'aadminn', 'aadmmiinn'])
    def test_repeated_chars(self, name):
        _blocked(name)

    # Unicode homoglyphs are caught via unidecode
    @pytest.mark.parametrize(
        'name',
        [
            '\u0430dmin',  # Cyrillic a
            '\u0430\u0434\u043c\u0438\u043d',  # full Cyrillic
            '\uff41\uff44\uff4d\uff49\uff4e',  # fullwidth
            '\u24d0\u24d3\u24dc\u24d8\u24dd',  # circled letters
        ],
    )
    def test_unicode_homoglyphs(self, name):
        _blocked(name)

    # invisible character insertion is caught
    @pytest.mark.parametrize('char', ['\u200b', '\u2060', '\ufe0f', '\u034f'])
    def test_invisible_chars(self, char):
        _blocked(f'ad{char}min')


class TestImpersonationCombos:
    # authority + protected name is blocked in both directions
    @pytest.mark.parametrize(
        'name',
        [
            'OfficialFurdu',
            'FurduOfficial',
            'AdminSouthernPaws',
            'FoxtailBot',
            'SystemFoxtail',
            'FoxtailMod',
            'StaffFurdu',
        ],
    )
    def test_direct_combos(self, name):
        _blocked(name)

    # authority + authority is blocked
    def test_authority_pair(self):
        _blocked('OfficialStaff')

    # combos with separators and filler words are blocked
    @pytest.mark.parametrize(
        'name',
        [
            'Official-Furdu',
            'Official_x_Furdu',
            'The Official Foxtail Team',
        ],
    )
    def test_padded_combos(self, name):
        _blocked(name)

    # leet-speak in authority terms is caught
    def test_leet_in_combo(self):
        _blocked('0fficial Furdu')


class TestFalsePositives:
    # legitimate names containing authority-term substrings are allowed
    @pytest.mark.parametrize(
        'name',
        [
            'Stafford',
            'SupportiveFox',
            'SystemOfADown',
            'OfficiallyDead',
            'Botany',
            'Modular',
            'Modifier',
            'RealTalk',
            'LifeSupport',
            'FireStaff',
            'Modsworth the Modest',
        ],
    )
    def test_legitimate_names(self, name):
        _allowed(name)

    # normal furry usernames are allowed
    @pytest.mark.parametrize(
        'name',
        [
            'fluffydragon',
            'kiwi_fox',
            'shadowpaws',
            'Fl00fy',
            'W0lf',
        ],
    )
    def test_normal_usernames(self, name):
        _allowed(name)
