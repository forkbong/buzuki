import yaml

from buzuki import DoesNotExist, InvalidNote
from buzuki.mixins import Model
from buzuki.utils import FLATS, SHARPS, distance, greeklish, to_unicode

with open('buzuki/scales.yml') as f:
    SCALES = yaml.safe_load(f.read())


class Scale(Model):
    def __init__(self, name, ascending, descending, chords):
        self.name = name
        self.ascending = ascending
        self.descending = descending
        self.chords = chords
        self.root = 'D'

    @classmethod
    def get(cls, name):
        """Scale constructor that takes the name of the scale."""
        key = greeklish(name)
        try:
            s = SCALES[key]
        except KeyError:
            raise DoesNotExist(f"Scale '{name}' does not exist")
        return cls(
            s.get('name'),
            s.get('ascending'),
            s.get('descending'),
            s.get('chords'),
        )

    @classmethod
    def all(cls):
        """Get a list with every scale."""
        return [cls.get(name) for name in SCALES]

    @property
    def slug(self):
        return greeklish(self.name)

    @property
    def info(self):
        """Return information about the scale."""
        stuff = [self.notes(), self.fretboard()]
        if self.descending is not None:
            stuff[0] = 'Άνοδος: ' + stuff[0]
            stuff.append('Κάθοδος: ' + self.notes(descending=True))
            stuff.append(self.fretboard(True))

        if self.chords:
            notes = self._get_notes_list()
            chords = []
            for chord in self.chords:
                index = int(chord[0]) - 1
                note = to_unicode(notes[index])
                chords.append(note + chord[1:])
            stuff.append('Βασικές συγχορδίες: ' + ', '.join(chords))

        return '\n\n'.join(stuff)

    @property
    def title(self):
        return f'{to_unicode(self.root)} {self.name}'

    def notes(self, descending=False):
        """Return a string with the notes of the scale."""
        notes = self._get_notes(descending)

        # If the root is sharp or flat, double signs can appear in the
        # scale. Try to avoid it by changing the root to an equivalent.
        if '##' in notes:
            idx = distance(self.root)
            self.root = FLATS[idx]
            alt = self._get_notes(descending)
            if 'bb' not in alt:
                notes = alt
            else:
                self.root = SHARPS[idx]
        elif 'bb' in notes:
            idx = distance(self.root)
            self.root = SHARPS[idx]
            alt = self._get_notes(descending)
            if '##' not in alt:
                notes = alt
            else:
                self.root = FLATS[idx]

        return to_unicode(notes)

    def fretboard(self, descending=False):
        """Display a fretboard with the notes of the scale."""
        scale = self.descending if descending else self.ascending
        fretboard = [
            '   ╔═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══╤',
            '   ║   │   │   │   │   │   │   │   │   │   │   │   │   │   │   │',
            '   ╟───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼',
            '   ║   │   │   │   │   │   │   │   │   │   │   │   │   │   │   │',
            '   ╚═══╧═══╧═o═╧═══╧═o═╧═══╧═o═╧═══╧═══╧═o═╧═══╧═o═╧═══╧═══╧═o═╧',
        ]
        notes = self._get_notes_list()
        # Show the first 15 frets plus the open string
        last = 15
        # Adjust the scale to start from the root
        scale = self._move(scale, distance(self.root))
        # Extend the scale for another octave
        scale = sorted(set(scale + self._move(scale, 12)))
        d_string = list(fretboard[0])
        a_string = list(fretboard[2])

        # 7 notes per octave, so in two octaves we have a maximum of 14 notes
        for i, di in enumerate(scale):
            ai = di + 5
            di %= 24  # Index in D string
            ai %= 24  # Index in A string
            note = notes[i % 7]
            assert len(note) in {1, 2, 3}
            if len(note) == 1:
                if di <= last:
                    d_string[4 * di + 1] = note
                if ai <= last:
                    a_string[4 * ai + 1] = note
            elif len(note) == 2:
                if di <= last:
                    d_string[4 * di + 1:4 * di + 3] = note
                if ai <= last:
                    a_string[4 * ai + 1:4 * ai + 3] = note
            elif len(note) == 3:
                if di <= last:
                    d_string[4 * di:4 * di + 3] = note
                if ai <= last:
                    a_string[4 * ai:4 * ai + 3] = note

        fretboard[0] = ''.join(d_string)
        fretboard[2] = ''.join(a_string)
        return to_unicode('\n'.join(fretboard))

    def _get_notes_list(self, descending=False):
        scale = self.descending if descending else self.ascending
        root = self.root
        notes = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        idx = notes.index(root[0])
        notes = notes[idx:] + notes[:idx]
        chromatic = SHARPS if root in SHARPS else FLATS
        try:
            idx = chromatic.index(root)
        except ValueError:
            raise InvalidNote(f"'{root}' is not a valid note")
        chromatic = chromatic[idx:] + chromatic[:idx]
        notes[0] = root
        for i, note in enumerate(notes):
            diff = scale[i] - chromatic.index(note)
            if diff > 0:
                notes[i] += diff * '#'
            elif diff < 0:
                notes[i] += -diff * 'b'
        notes.append(notes[0])
        return notes

    def _get_notes(self, descending=False):
        return ' '.join(self._get_notes_list(descending))

    def _move(self, frets, offset):
        """Move the scale right by `offset` frets."""
        return [fret + offset for fret in frets]
