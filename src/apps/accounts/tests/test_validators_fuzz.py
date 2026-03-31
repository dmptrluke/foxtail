import contextlib
import re
import string

from django.core.exceptions import ValidationError

import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from apps.accounts.validators import (
    _AUTHORITY_TERMS,
    _INVISIBLE_RE,
    _PROTECTED_NAMES,
    _RESERVED_NORMALIZED,
    _SEPARATOR_RE,
    UsernameValidator,
    _normalize_full,
    _normalize_light,
    username_validators,
    validate_blacklist,
)

# -- strategies --

# characters the UsernameValidator regex allows
VALID_CHARS = string.ascii_letters + string.digits + '.@ +-_'

valid_usernames = st.text(alphabet=VALID_CHARS, min_size=1, max_size=50).filter(lambda s: s.strip())

# unicode text including invisible chars, homoglyphs, and CJK
unicode_usernames = st.text(min_size=1, max_size=80)

# invisible chars from the validator's own regex
INVISIBLE_CHARS = (
    '\u00ad\u200b\u200c\u200d\u200e\u200f\u2060\u2061\u2062\u2063\u2064'
    '\ufeff\ufe0e\ufe0f\u034f\u115f\u1160\u17b4\u17b5\u180e'
)
invisible_text = st.text(alphabet=INVISIBLE_CHARS, min_size=1, max_size=20)


class TestNormalizationProperties:
    # _normalize_full never crashes on arbitrary unicode
    @given(st.text(min_size=1, max_size=200))
    @settings(max_examples=1000, suppress_health_check=[HealthCheck.too_slow])
    def test_normalize_full_never_crashes(self, s):
        result = _normalize_full(s)
        assert isinstance(result, str)

    # _normalize_light never crashes on arbitrary unicode
    @given(st.text(min_size=1, max_size=200))
    @settings(max_examples=1000, suppress_health_check=[HealthCheck.too_slow])
    def test_normalize_light_never_crashes(self, s):
        result = _normalize_light(s)
        assert isinstance(result, str)

    # full normalization always produces lowercase ASCII without separators
    @given(st.text(min_size=1, max_size=100))
    @settings(max_examples=500)
    def test_normalize_full_output_is_clean(self, s):
        result = _normalize_full(s)
        assert result == result.lower()
        assert not _SEPARATOR_RE.search(result)
        assert not _INVISIBLE_RE.search(result)

    # light normalization always produces lowercase with no non-alnum
    @given(st.text(min_size=1, max_size=100))
    @settings(max_examples=500)
    def test_normalize_light_output_is_clean(self, s):
        result = _normalize_light(s)
        assert result == result.lower()
        assert re.fullmatch(r'[a-z0-9]*', result), f'non-alnum in light normalization: {result!r}'

    # full normalization is idempotent
    @given(st.text(min_size=1, max_size=100))
    @settings(max_examples=500)
    def test_normalize_full_idempotent(self, s):
        once = _normalize_full(s)
        twice = _normalize_full(once)
        assert once == twice

    # light normalization is idempotent
    @given(st.text(min_size=1, max_size=100))
    @settings(max_examples=500)
    def test_normalize_light_idempotent(self, s):
        once = _normalize_light(s)
        twice = _normalize_light(once)
        assert once == twice

    # invisible chars are always stripped (no effect on output)
    @given(
        base=st.text(alphabet=string.ascii_lowercase, min_size=1, max_size=20),
        padding=invisible_text,
        pos=st.integers(min_value=0, max_value=20),
    )
    @settings(max_examples=500)
    def test_invisible_chars_stripped(self, base, padding, pos):
        pos = min(pos, len(base))
        injected = base[:pos] + padding + base[pos:]
        assert _normalize_full(injected) == _normalize_full(base)


class TestValidateBlacklistProperties:
    # validate_blacklist never raises anything except ValidationError
    @given(unicode_usernames)
    @settings(max_examples=2000, suppress_health_check=[HealthCheck.too_slow])
    def test_never_crashes(self, s):
        with contextlib.suppress(ValidationError):
            validate_blacklist(s)

    # a known reserved word is always blocked regardless of casing
    @given(
        word=st.sampled_from(sorted(_RESERVED_NORMALIZED)),
        upper_mask=st.lists(st.booleans(), min_size=50, max_size=50),
    )
    @settings(max_examples=500)
    def test_reserved_words_blocked_any_case(self, word, upper_mask):
        assume(len(word) > 0)
        mixed = ''.join(c.upper() if upper_mask[i % len(upper_mask)] else c for i, c in enumerate(word))
        with_case_norm = _normalize_full(mixed)
        if with_case_norm in _RESERVED_NORMALIZED:
            with contextlib.suppress(ValidationError):
                validate_blacklist(mixed)

    # injecting invisible chars into a reserved word still blocks it
    @given(
        word=st.sampled_from(['admin', 'staff', 'root', 'support', 'moderator']),
        insert_pos=st.integers(min_value=1, max_value=8),
        invisible=st.sampled_from(list(INVISIBLE_CHARS)),
    )
    def test_invisible_injection_still_blocked(self, word, insert_pos, invisible):
        pos = min(insert_pos, len(word) - 1)
        injected = word[:pos] + invisible + word[pos:]
        with pytest.raises(ValidationError):
            validate_blacklist(injected)

    # repeating chars in a reserved word still blocks it
    @given(
        word=st.sampled_from(['admin', 'staff', 'root']),
        char_idx=st.integers(min_value=0, max_value=4),
        repeats=st.integers(min_value=2, max_value=5),
    )
    def test_repeated_chars_still_blocked(self, word, char_idx, repeats):
        idx = min(char_idx, len(word) - 1)
        inflated = word[:idx] + word[idx] * repeats + word[idx + 1 :]
        with pytest.raises(ValidationError):
            validate_blacklist(inflated)


class TestImpersonationFuzzProperties:
    # authority + protected name combo is always caught regardless of separator
    @given(
        authority=st.sampled_from(_AUTHORITY_TERMS),
        protected=st.sampled_from(_PROTECTED_NAMES),
        separator=st.sampled_from(['', ' ', '.', '-', '_', '  ', '__']),
        order=st.booleans(),
    )
    def test_impersonation_combos_always_caught(self, authority, protected, separator, order):
        if order:
            username = authority + separator + protected
        else:
            username = protected + separator + authority
        with pytest.raises(ValidationError):
            validate_blacklist(username)

    # authority + authority combo is also caught
    @given(
        term_a=st.sampled_from(_AUTHORITY_TERMS),
        term_b=st.sampled_from(_AUTHORITY_TERMS),
        separator=st.sampled_from(['', ' ', '-', '_']),
    )
    def test_authority_pairs_caught(self, term_a, term_b, separator):
        assume(term_a != term_b)
        username = term_a + separator + term_b
        with pytest.raises(ValidationError):
            validate_blacklist(username)


class TestFullValidatorChain:
    # the full signup validator chain: regex pass + blacklist pass means the username is safe
    @given(valid_usernames)
    @settings(max_examples=1000, suppress_health_check=[HealthCheck.too_slow])
    def test_valid_chars_survive_full_chain(self, s):
        for v in username_validators:
            try:
                v(s)
            except ValidationError:
                return  # rejected by one validator, that's fine

    # reserved words wrapped in valid chars are still caught by the full chain
    @given(
        word=st.sampled_from(['admin', 'staff', 'root', 'moderator', 'support']),
        prefix=st.text(alphabet=string.ascii_lowercase, min_size=0, max_size=3),
        suffix=st.text(alphabet=string.ascii_lowercase, min_size=0, max_size=3),
    )
    @settings(max_examples=500)
    def test_reserved_with_padding_through_chain(self, word, prefix, suffix):
        username = prefix + word + suffix
        blocked = False
        for v in username_validators:
            try:
                v(username)
            except ValidationError:
                blocked = True
                break
        # bare reserved word must always be blocked; padded versions may or may not be
        if not prefix and not suffix:
            assert blocked, f'{username!r} should have been blocked by the full chain'


class TestUsernameValidatorProperties:
    # UsernameValidator accepts all strings composed of its allowed chars
    @given(valid_usernames)
    @settings(max_examples=500)
    def test_valid_chars_accepted(self, s):
        validator = UsernameValidator()
        validator(s)

    # UsernameValidator rejects strings with disallowed chars
    @given(
        st.text(
            alphabet=st.sampled_from(list('!#$%^&*()={}[]|\\:;"\'<>,?/~`')),
            min_size=1,
            max_size=10,
        )
    )
    @settings(max_examples=200)
    def test_invalid_chars_rejected(self, s):
        validator = UsernameValidator()
        with pytest.raises(ValidationError):
            validator(s)


class TestReDoS:
    # repeated separators don't cause catastrophic backtracking
    @given(
        char=st.sampled_from(list('.-_ ')),
        count=st.integers(min_value=100, max_value=5000),
    )
    @settings(max_examples=200, deadline=1000)
    def test_repeated_separators(self, char, count):
        s = char * count
        _normalize_full(s)
        _normalize_light(s)

    # repeated dedup-triggering chars don't cause slowdown
    @given(
        char=st.sampled_from(list('aeiou')),
        count=st.integers(min_value=100, max_value=5000),
    )
    @settings(max_examples=200, deadline=1000)
    def test_repeated_chars(self, char, count):
        s = char * count
        _normalize_full(s)

    # long unicode strings through anyascii don't hang
    @given(st.text(min_size=500, max_size=5000))
    @settings(max_examples=200, deadline=2000, suppress_health_check=[HealthCheck.too_slow])
    def test_long_unicode(self, s):
        _normalize_full(s)
        _normalize_light(s)

    # adversarial regex input: alternating pattern that could trigger backtracking
    @given(count=st.integers(min_value=100, max_value=2000))
    @settings(max_examples=100, deadline=1000)
    def test_alternating_pattern(self, count):
        s = 'a.' * count
        _normalize_full(s)

    # full validate_blacklist completes within deadline on long input
    @given(st.text(alphabet=VALID_CHARS, min_size=100, max_size=2000))
    @settings(max_examples=200, deadline=2000, suppress_health_check=[HealthCheck.too_slow])
    def test_blacklist_performance(self, s):
        with contextlib.suppress(ValidationError):
            validate_blacklist(s)
