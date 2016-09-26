import re

SHARPS = ['D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'C', 'C#']
FLATS = ['D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B', 'C', 'Db']


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


def greeklish(string, sep=None):
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
    gr_chars = 'αβγδεζηικλμνοπρσςτυφχωάέήίόύώϊΐ'
    en_chars = 'avgdeziiklmnoprsstyfxoaeiioyoii'
    table = str.maketrans(gr_chars, en_chars)
    string = string.translate(table)

    # Separator
    if sep is not None:
        string = re.sub(' ', sep, string)

    # Remove all the rest. Assumes separators are either
    # spaces or underscores and should explicitly
    # use `sep` if something else were possible.
    string = re.sub('[^a-z_ ]', '', string)

    return string
