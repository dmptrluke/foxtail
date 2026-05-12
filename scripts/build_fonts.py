"""Build subsetted web fonts for self-hosting.

Run:
    uv run --with 'fonttools[woff]' --with brotli python scripts/build_fonts.py
"""

from __future__ import annotations

import io
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / '.cache' / 'fonts'
FONTS_OUT = ROOT / 'assets' / 'fonts'

INTER_VERSION = '4.1'
INTER_ZIP_URL = f'https://github.com/rsms/inter/releases/download/v{INTER_VERSION}/Inter-{INTER_VERSION}.zip'

# The base latin subset includes te reo Maori macron letters that would
# normally live in latin-ext. That keeps common NZ text from triggering an
# extra font request for a handful of codepoints.
LATIN = (
    'U+0000-00FF,U+0100-0101,U+0112-0113,U+012A-012B,'
    'U+014C-014D,U+016A-016B,U+0131,U+0152-0153,U+02BB-02BC,'
    'U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,'
    'U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD'
)
LATIN_EXT = (
    'U+0102-0111,U+0114-0129,U+012C-0149,U+014A-014B,'
    'U+014E-0169,U+016C-02BA,U+02BD-02C5,U+02C7-02CC,'
    'U+02CE-02D7,U+02DD-02FF,U+1D00-1DBF,U+1E00-1E9F,'
    'U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,'
    'U+2113,U+2C60-2C7F,U+A720-A7FF'
)
SUBSETS = {'latin': LATIN, 'latin-ext': LATIN_EXT}

FEATURES = {
    'inter': 'kern,mark,mkmk,ccmp,calt,locl,sups,subs,tnum,zero,cv13',
    'plus-jakarta-sans': 'kern,mark,ccmp,calt,liga,locl,sups,subs,tnum',
    'ibm-plex-mono': 'ccmp,mark',
}

SOURCES = [
    {
        'name': 'inter',
        'files': [
            ('wght', 'normal', '', 'InterVariable.ttf'),
            ('wght', 'italic', '', 'InterVariable-Italic.ttf'),
        ],
    },
    {
        'name': 'plus-jakarta-sans',
        'files': [
            (
                'wght',
                'normal',
                'https://github.com/google/fonts/raw/main/ofl/plusjakartasans/PlusJakartaSans%5Bwght%5D.ttf',
                'PlusJakartaSans[wght].ttf',
            ),
            (
                'wght',
                'italic',
                'https://github.com/google/fonts/raw/main/ofl/plusjakartasans/PlusJakartaSans-Italic%5Bwght%5D.ttf',
                'PlusJakartaSans-Italic[wght].ttf',
            ),
        ],
    },
    {
        'name': 'ibm-plex-mono',
        'files': [
            (
                '400',
                'normal',
                'https://github.com/google/fonts/raw/main/ofl/ibmplexmono/IBMPlexMono-Regular.ttf',
                'IBMPlexMono-Regular.ttf',
            ),
            (
                '400',
                'italic',
                'https://github.com/google/fonts/raw/main/ofl/ibmplexmono/IBMPlexMono-Italic.ttf',
                'IBMPlexMono-Italic.ttf',
            ),
            (
                '600',
                'normal',
                'https://github.com/google/fonts/raw/main/ofl/ibmplexmono/IBMPlexMono-SemiBold.ttf',
                'IBMPlexMono-SemiBold.ttf',
            ),
            (
                '600',
                'italic',
                'https://github.com/google/fonts/raw/main/ofl/ibmplexmono/IBMPlexMono-SemiBoldItalic.ttf',
                'IBMPlexMono-SemiBoldItalic.ttf',
            ),
        ],
    },
]

VERIFY_CODEPOINTS = {'latin': [0x0041, 0x0100], 'latin-ext': [0x0102]}


def download(url: str, dest: Path, label: str) -> None:
    """Download a source file if it is not already cached."""
    if dest.exists():
        return

    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f'Downloading {label}...', flush=True)  # noqa: T201
    with urllib.request.urlopen(url) as response:  # noqa: S310
        dest.write_bytes(response.read())


def download_inter() -> None:
    """Download the Inter variable fonts from the release archive.
    It's a special case because I want variable fonts and full OpenType features."""
    cache_dir = CACHE / 'inter'
    normal = cache_dir / 'InterVariable.ttf'
    italic = cache_dir / 'InterVariable-Italic.ttf'
    if normal.exists() and italic.exists():
        return

    cache_dir.mkdir(parents=True, exist_ok=True)
    print(f'Downloading Inter {INTER_VERSION}...', flush=True)  # noqa: T201
    with urllib.request.urlopen(INTER_ZIP_URL) as response:  # noqa: S310
        data = response.read()

    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for name in archive.namelist():
            target = {'InterVariable.ttf': normal, 'InterVariable-Italic.ttf': italic}.get(Path(name).name)
            if target is not None:
                target.write_bytes(archive.read(name))

    if not normal.exists() or not italic.exists():
        raise RuntimeError('Inter variable fonts were not found in the release archive.')


def cache_sources() -> None:
    """Download all source fonts into the local cache."""
    download_inter()
    for font in SOURCES:
        if font['name'] == 'inter':
            continue
        for weight, style, url, filename in font['files']:
            download(url, CACHE / font['name'] / filename, f'{font["name"]} {weight} {style}')


def subset(src: Path, out: Path, unicodes: str, features: str) -> None:
    """Write a WOFF2 subset for one source font."""
    out.parent.mkdir(parents=True, exist_ok=True)
    print(f'Subsetting {out.name}...', flush=True)  # noqa: T201
    subprocess.run(  # noqa: S603
        [
            sys.executable,
            '-m',
            'fontTools.subset',
            str(src),
            f'--unicodes={unicodes}',
            f'--layout-features={features}',
            '--flavor=woff2',
            f'--output-file={out}',
        ],
        check=True,
    )


def build_fonts() -> None:
    """Generate every configured subset."""
    for font in SOURCES:
        for weight, style, _url, filename in font['files']:
            src = CACHE / font['name'] / filename
            for subset_name, unicodes in SUBSETS.items():
                out = FONTS_OUT / f'{font["name"]}-{subset_name}-{weight}-{style}.woff2'
                subset(src, out, unicodes, FEATURES[font['name']])


def verify_font(path: Path, subset_name: str) -> list[str]:
    """Return validation errors for one generated font."""
    from fontTools.ttLib import TTFont

    if not path.exists():
        return [f'missing: {path.name}']
    if path.stat().st_size < 1000:
        return [f'too small: {path.name}']

    try:
        cmap = TTFont(str(path)).getBestCmap()
    except Exception as exc:  # noqa: BLE001
        return [f'cannot open {path.name}: {exc}']

    return [
        f'U+{codepoint:04X} missing from {path.name}'
        for codepoint in VERIFY_CODEPOINTS[subset_name]
        if codepoint not in cmap
    ]


def verify_fonts() -> None:
    """Check that generated files exist and contain expected codepoints."""
    errors = []
    for font in SOURCES:
        for weight, style, _url, _filename in font['files']:
            for subset_name in SUBSETS:
                path = FONTS_OUT / f'{font["name"]}-{subset_name}-{weight}-{style}.woff2'
                errors.extend(verify_font(path, subset_name))

    if errors:
        raise SystemExit('\n'.join(errors))


def main() -> None:
    cache_sources()
    build_fonts()
    verify_fonts()
    print('Done.', flush=True)  # noqa: T201


if __name__ == '__main__':
    main()
