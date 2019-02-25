import pytest

from buzuki import InvalidNote
from buzuki.scales import Scale


def test_info():
    scale = Scale.get('karsigar')
    scale.root = 'E'
    assert scale.name == 'Καρσιγάρ'
    assert scale.slug == 'karsigar'
    assert scale.info == """\
E F♯ G A B♭ C♯ D E

 D ╔═══╤═E═╤═══╤═F♯╤═G═╤═══╤═A═╤═B♭╤═══╤═══╤═C♯╤═D═╤═══╤═E═╤═══╤
   ║   │   │   │   │   │   │   │   │   │   │   │   │   │   │   │
 A ╟─B♭┼───┼───┼─C♯┼─D─┼───┼─E─┼───┼─F♯┼─G─┼───┼─A─┼─B♭┼───┼───┼
   ║   │   │   │   │   │   │   │   │   │   │   │   │   │   │   │
   ╚═══╧═══╧═o═╧═══╧═o═╧═══╧═o═╧═══╧═══╧═o═╧═══╧═o═╧═══╧═══╧═o═╧

Βασικές συγχορδίες: Em, Gm, A, D, Dm"""


@pytest.mark.parametrize('name, root, fretboard', [
    ('armoniko minore', 'D',  """\
 D ╔═══╤═E═╤═F═╤═══╤═G═╤═══╤═A═╤═B♭╤═══╤═══╤═C♯╤═D═╤═══╤═E═╤═F═╤
   ║   │   │   │   │   │   │   │   │   │   │   │   │   │   │   │
 A ╟─B♭┼───┼───┼─C♯┼─D─┼───┼─E─┼─F─┼───┼─G─┼───┼─A─┼─B♭┼───┼───┼
   ║   │   │   │   │   │   │   │   │   │   │   │   │   │   │   │
   ╚═══╧═══╧═o═╧═══╧═o═╧═══╧═o═╧═══╧═══╧═o═╧═══╧═o═╧═══╧═══╧═o═╧"""),
    ('armoniko minore', 'E',  """\
   ╔═D♯╤═E═╤═══╤═F♯╤═G═╤═══╤═A═╤═══╤═B═╤═C═╤═══╤═══╤═D♯╤═E═╤═══╤
   ║   │   │   │   │   │   │   │   │   │   │   │   │   │   │   │
 A ╟───┼─B─┼─C─┼───┼───┼─D♯┼─E─┼───┼─F♯┼─G─┼───┼─A─┼───┼─B─┼─C─┼
   ║   │   │   │   │   │   │   │   │   │   │   │   │   │   │   │
   ╚═══╧═══╧═o═╧═══╧═o═╧═══╧═o═╧═══╧═══╧═o═╧═══╧═o═╧═══╧═══╧═o═╧"""),
    ('armoniko minore', 'Eb',  """\
 D ╔═E♭╤═══╤═F═╤═G♭╤═══╤═A♭╤═══╤═B♭╤═C♭╤═══╤═══╤═D═╤═E♭╤═══╤═F═╤
   ║   │   │   │   │   │   │   │   │   │   │   │   │   │   │   │
   ╟─B♭┼─C♭┼───┼───┼─D─┼─E♭┼───┼─F─┼─G♭┼───┼─A♭┼───┼─B♭┼─C♭┼───┼
   ║   │   │   │   │   │   │   │   │   │   │   │   │   │   │   │
   ╚═══╧═══╧═o═╧═══╧═o═╧═══╧═o═╧═══╧═══╧═o═╧═══╧═o═╧═══╧═══╧═o═╧"""),
    ('armoniko minore', 'A',  """\
 D ╔═══╤═E═╤═F═╤═══╤═══╤═G♯╤═A═╤═══╤═B═╤═C═╤═══╤═D═╤═══╤═E═╤═F═╤
   ║   │   │   │   │   │   │   │   │   │   │   │   │   │   │   │
 A ╟───┼─B─┼─C─┼───┼─D─┼───┼─E─┼─F─┼───┼───┼─G♯┼─A─┼───┼─B─┼─C─┼
   ║   │   │   │   │   │   │   │   │   │   │   │   │   │   │   │
   ╚═══╧═══╧═o═╧═══╧═o═╧═══╧═o═╧═══╧═══╧═o═╧═══╧═o═╧═══╧═══╧═o═╧"""),
    ('niavent', 'Db',  """\
   ╔═E♭╤═F♭╤═══╤═══╤═G═╤═A♭╤B♭♭╤═══╤═══╤═C═╤═D♭╤═══╤═E♭╤═F♭╤═══╤
   ║   │   │   │   │   │   │   │   │   │   │   │   │   │   │   │
B♭♭╟───┼───┼─C─┼─D♭┼───┼─E♭┼─F♭┼───┼───┼─G─┼─A♭┼B♭♭┼───┼───┼─C─┼
   ║   │   │   │   │   │   │   │   │   │   │   │   │   │   │   │
   ╚═══╧═══╧═o═╧═══╧═o═╧═══╧═o═╧═══╧═══╧═o═╧═══╧═o═╧═══╧═══╧═o═╧"""),
    ('karsigar', 'E',  """\
 D ╔═══╤═E═╤═══╤═F♯╤═G═╤═══╤═A═╤═B♭╤═══╤═══╤═C♯╤═D═╤═══╤═E═╤═══╤
   ║   │   │   │   │   │   │   │   │   │   │   │   │   │   │   │
 A ╟─B♭┼───┼───┼─C♯┼─D─┼───┼─E─┼───┼─F♯┼─G─┼───┼─A─┼─B♭┼───┼───┼
   ║   │   │   │   │   │   │   │   │   │   │   │   │   │   │   │
   ╚═══╧═══╧═o═╧═══╧═o═╧═══╧═o═╧═══╧═══╧═o═╧═══╧═o═╧═══╧═══╧═o═╧"""),
])
def test_fretboard(name, root, fretboard):
    scale = Scale.get(name)
    scale.root = root
    assert scale.fretboard() == fretboard


@pytest.mark.parametrize('name, root, notes', [
    ('matzore', 'D', 'D E F♯ G A B C♯ D'),
    ('matzore', 'Db', 'D♭ E♭ F G♭ A♭ B♭ C D♭'),
    ('matzore', 'C#', 'C♯ D♯ E♯ F♯ G♯ A♯ B♯ C♯'),
    ('sampax', 'D', 'D E F G♭ A B♭ C D'),
    ('sampax', 'C#', 'C♯ D♯ E F G♯ A B C♯'),
    ('sampax', 'Db', 'C♯ D♯ E F G♯ A B C♯'),
    ('niavent', 'D', 'D E F G♯ A B♭ C♯ D'),
    ('niavent', 'C#', 'C♯ D♯ E F♯♯ G♯ A B♯ C♯'),
    ('niavent', 'Db', 'D♭ E♭ F♭ G A♭ B♭♭ C D♭'),
    ('segkiax', 'D', 'D E♯ F♯ G A B C♯ D'),
    ('segkiax', 'C#', 'D♭ E F G♭ A♭ B♭ C D♭'),
    ('segkiax', 'Db', 'D♭ E F G♭ A♭ B♭ C D♭'),
])
def test_notes(name, root, notes):
    scale = Scale.get(name)
    scale.root = root
    assert scale.notes() == notes


def test_all():
    assert len(Scale.all()) == 16


def test_invalid_root():
    scale = Scale.get('rast')
    scale.root = 'Fb'
    with pytest.raises(InvalidNote):
        scale.info
