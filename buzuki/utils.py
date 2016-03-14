import os
import re

from flask import current_app


class Transposer:
    """Chord transposer.

    Class attributes:
        SHARPS: Chromatic scale with sharps.
        FLATS: Chromatic scale with flats.

    Attributes:
        song: A string with the song to transpose.
        num: Number of semitones to transpose `song` by.
        notes: The possible root notes of the chords in `song`.
        _carry: Number of spaces that need adjustment in the next chord
                replacement.
    """

    SHARPS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    FLATS = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

    def __init__(self, song):
        self.num = 0
        self.notes = self.get_notes(song)
        self.song = song.split('\n')
        self._carry = 0

    def get_notes(self, song):
        """Find if `song` uses sharps or flats."""
        if re.search(r'[DEGAB]b', song) is not None:
            return self.FLATS
        else:
            return self.SHARPS

    def transpose(self, num):
        """Transpose `self.song` by `num` semitones."""
        self.num = num
        pattern = r'([A-G][#b]?)([^A-G\s]*)(\s*)'
        new_song = []
        for line in self.song:
            new_line = re.sub(pattern, self.chordrepl, line)
            new_song.append(new_line.rstrip())
            self._carry = 0
        return '\n'.join(new_song)

    def chordrepl(self, matchobj):
        """Chord replace function."""
        note = matchobj.group(1)
        chord = matchobj.group(2)
        spaces = len(matchobj.group(3))
        # FIXME: Raises ValueError if a song has both sharps and flats
        idx = (self.notes.index(note) + self.num) % 12
        new = self.notes[idx]
        self._carry += len(note) - len(new)
        self._carry, spaces = sorted((0, self._carry + spaces))
        return ''.join([new, chord, ' ' * spaces])


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


def export_song(song, directory=None):
    directory = directory or current_app.config['SONGDIR']
    os.makedirs(directory, mode=0o755, exist_ok=True)
    path = os.path.join(directory, song.slug)
    with open(path, 'w') as f:
        content = [song.name, song.artist, song.link, '', song.body, '']
        f.write('\n'.join(content))
