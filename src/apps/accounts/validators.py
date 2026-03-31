import json
import re
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from anyascii import anyascii

_LEET_MAP = str.maketrans('013457@$!', 'oieastasi')

# invisible/zero-width characters to strip before any processing
_INVISIBLE_RE = re.compile(
    '[\u00ad\u200b\u200c\u200d\u200e\u200f\u2060\u2061\u2062\u2063\u2064'
    '\ufeff\ufe0e\ufe0f\u034f\u115f\u1160\u17b4\u17b5\u180e]'
)
_SEPARATOR_RE = re.compile(r'[\s._-]')
_DEDUP_RE = re.compile(r'(.)\1+')
_NON_ALNUM_RE = re.compile(r'[^a-z0-9]')

_DATA_FILE = Path(__file__).parent / 'data' / 'reserved_usernames.json'
_RESERVED_RAW = frozenset(json.loads(_DATA_FILE.read_text()))

# pre-normalize the reserved list: strip separators, deleet, collapse repeated chars
_RESERVED_NORMALIZED = frozenset(
    _DEDUP_RE.sub(r'\1', _SEPARATOR_RE.sub('', w).translate(_LEET_MAP)) for w in _RESERVED_RAW
)

_AUTHORITY_TERMS = [
    'admin',
    'bot',
    'mod',
    'moderator',
    'official',
    'staff',
    'support',
    'system',
    'thereal',
    'verified',
]

_PROTECTED_NAMES = [
    # site identity
    'foxtail',
    'furrynz',
    # NZ conventions
    'furconz',
    'southernpaws',
    'nzpah',
    # AU conventions
    'furdu',
    'furrydownunder',
    'aurawra',
    'melbournefurcon',
    'mfc',
    'furjam',
    'confurgence',
    # major worldwide conventions
    'anthrocon',
    'midwestfurfest',
    'furryweekendatlanta',
    'fwa',
    'blfc',
    'furtherconfusion',
    'megaplex',
    'furnalequinox',
    'denfur',
    'vancoufur',
    'eurofurence',
    'nordicfuzzcon',
    'confuzzled',
    # furry platforms
    'furaffinity',
    'e621',
    'barq',
    'inkbunny',
]


def _normalize_full(value):
    """Fold a username with all layers including dedup (for reserved list check)."""
    cleaned = _INVISIBLE_RE.sub('', value)
    ascii_folded = anyascii(cleaned).lower()
    stripped = _SEPARATOR_RE.sub('', ascii_folded)
    deleeted = stripped.translate(_LEET_MAP)
    return _DEDUP_RE.sub(r'\1', deleeted)


def _normalize_light(value):
    """Fold without dedup or leet-mapping (for impersonation combo check)."""
    cleaned = _INVISIBLE_RE.sub('', value)
    ascii_folded = anyascii(cleaned).lower()
    return _NON_ALNUM_RE.sub('', ascii_folded)


def _has_impersonation_combo(normalized):
    """Check if the normalized username contains both an authority term and a protected name."""
    search_terms = _PROTECTED_NAMES + _AUTHORITY_TERMS
    for authority in _AUTHORITY_TERMS:
        if authority not in normalized:
            continue
        remainder = normalized.replace(authority, '', 1)
        if any(t != authority and t in remainder for t in search_terms):
            return True
    return False


def validate_blacklist(value):
    normalized = _normalize_full(value)

    if normalized in _RESERVED_NORMALIZED:
        raise ValidationError(
            'This username is not allowed.',
            params={'value': value},
        )

    pre_leet = _normalize_light(value)
    post_leet = pre_leet.translate(_LEET_MAP)
    if _has_impersonation_combo(pre_leet) or _has_impersonation_combo(post_leet):
        raise ValidationError(
            'This username is not allowed.',
            params={'value': value},
        )


class UsernameValidator(RegexValidator):
    regex = r'^[\w.@ +-]+\Z'
    message = 'Enter a valid username. This value may contain only letters, spaces, numbers, and @/./+/-/_ characters.'

    flags = 0


username_validators = [UsernameValidator(), validate_blacklist]
