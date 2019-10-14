import re
import unicodedata

from buzuki import InvalidNote

SHARPS = ['D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#']
FLATS = ['D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B', 'C', 'Db']


def distance(note: str) -> int:
    """Return the distance of the note from D, in semitones.

    Does not work with double sharps/flats.
    """
    if note in SHARPS:
        return SHARPS.index(note)
    elif note in FLATS:
        return FLATS.index(note)
    else:
        raise InvalidNote(f"'{note}' is not a valid note")


def transpose(song: str, num: int) -> str:
    """Transpose `song` by `num` semitones."""
    def chordrepl(matchobj):
        """Chord replace function."""
        nonlocal carry
        note = matchobj.group(1)
        chord = matchobj.group(2)
        spaces = len(matchobj.group(3))
        # FIXME: Raises ValueError if a song has both sharps and flats
        idx = (notes.index(note) + num) % 12
        new = notes[idx]
        carry += len(note) - len(new)
        carry, spaces = sorted((0, carry + spaces))
        return ''.join([new, chord, ' ' * spaces])

    # FIXME: Assumes that both sharp and flat notes cannot coexist
    notes = FLATS if re.search(r'[DEGAB]b', song) else SHARPS
    lines = song.split('\n')
    pattern = r'([A-G][#b]?)([^A-G\s]*)(\s*)'
    new_song = []
    for line in lines:
        carry = 0
        new_line = re.sub(pattern, chordrepl, line)
        new_song.append(new_line.rstrip())
    return '\n'.join(new_song)


def transpose_to_root(song: str, old_root: str, new_root: str) -> str:
    """Transpose `song` to `root`."""
    diff = distance(new_root) - distance(old_root)
    return transpose(song, diff)


def greeklish(string: str) -> str:
    """Create greeklish slugs."""
    string = string.lower()

    # Digraphs
    string = re.sub('ψ', 'ps', string)
    string = re.sub('ξ', 'ks', string)
    string = re.sub('θ', 'th', string)
    string = re.sub('ο[υύ]', 'ou', string)
    string = re.sub('α[υύ]', 'au', string)
    string = re.sub('ε[υύ]', 'eu', string)

    # Rest letters
    gr_chars = 'αβγδεζηικλμνοπρσςτυφχωάέήίόύώϊΐ '
    en_chars = 'avgdeziiklmnoprsstyfxoaeiioyoii_'
    table = str.maketrans(gr_chars, en_chars)
    string = string.translate(table)

    # Remove all the rest.
    string = re.sub('[^a-z_]', '', string)

    return string


def unaccented(string: str) -> str:
    """Return `string` lowercase and unaccented."""
    string = string.lower()
    return re.sub(r'[\u0300-\u036f]', '', unicodedata.normalize('NFD', string))


def to_unicode(string: str) -> str:
    """Use a dedicated unicode symbol for sharps and flats."""
    # FIXME: We assume that songs are greek and there will be no 'b' in lyrics
    string = re.sub('b', '♭', string)
    string = re.sub('#', '♯', string)
    return string
