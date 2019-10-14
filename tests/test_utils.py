from textwrap import dedent

import pytest

from buzuki import InvalidNote
from buzuki.utils import distance, greeklish, transpose, unaccented


def test_distance():
    assert distance('D') == 0
    assert distance('D#') == 1
    assert distance('E') == 2
    assert distance('F') == 3
    assert distance('F#') == 4
    assert distance('Eb') == 1
    assert distance('Gb') == 4
    with pytest.raises(InvalidNote):
        distance('E#')
    with pytest.raises(InvalidNote):
        distance('Fb')
    with pytest.raises(InvalidNote):
        distance('G##')
    with pytest.raises(InvalidNote):
        distance('asdf')


class TestTraspose:

    @pytest.mark.parametrize('semitones, expected', [
        (13, 'A#A#A#AD#dim   D7'),
        (12, 'AAA G# Ddim    C#7'),
        (-1, 'G#G#G#GC#dim   C7'),
        (-2, 'GGG F# Cdim    B7'),
    ])
    def test_transpose_sharps(self, semitones, expected):
        assert transpose('AAA G# Ddim    C#7', semitones) == expected

    @pytest.mark.parametrize('semitones, expected', [
        (13, 'BbBbBbAEbdim   D7'),
        (12, 'AAA Ab Ddim    Db7'),
        (-1, 'AbAbAbGDbdim   C7'),
        (-2, 'GGG Gb Cdim    B7'),
    ])
    def test_transpose_flats(self, semitones, expected):
        assert transpose('AAA Ab Ddim    Db7', semitones) == expected

    def test_song(self):
        original = dedent("""\
            Τα μπλε παράθυρά σου

            Bm  Bm  F#  Bm   | 4x

            D
            Περνούσα και σ' αντίκρυζα ψηλά στα παραθύρια   | 2x
            Em
            και τότες πια καμάρωνα τα δυο σου μαύρα φρύδια
            Em                        F#            Bm
            και τότες πια καμάρωνα τα δυο σου μαύρα φρύδια
            """)
        one_up = dedent("""\
            Τα μπλε παράθυρά σου

            Cm  Cm  G   Cm   | 4x

            D#
            Περνούσα και σ' αντίκρυζα ψηλά στα παραθύρια   | 2x
            Fm
            και τότες πια καμάρωνα τα δυο σου μαύρα φρύδια
            Fm                        G             Cm
            και τότες πια καμάρωνα τα δυο σου μαύρα φρύδια
            """)
        transposed = transpose(original, 1)
        assert transposed == one_up

    def test_untransposable(self):
        # Currently doesn't work for a song with both sharps and flats
        original = "A# Bb"
        with pytest.raises(ValueError):
            transpose(original, 1)


@pytest.mark.parametrize('string, expected', [
    ('ασδφ', 'asdf'),
    ('τεστ τεστ', 'test_test'),
    ('Τουτ\' οι μπάτσοι', 'tout_oi_mpatsoi'),
    ('Γιατί φουμάρω κοκαΐνη', 'giati_foumaro_kokaini'),
])
def test_greeklish(string, expected):
    assert greeklish(string) == expected


@pytest.mark.parametrize('string, expected', [
    ('ασδφ', 'ασδφ'),
    ('τεστ τεστ', 'τεστ τεστ'),
    ('Τουτ\' οι μπάτσοι', 'τουτ\' οι μπατσοι'),
    ('Γιατί φουμάρω κοκαΐνη', 'γιατι φουμαρω κοκαινη'),
])
def test_unaccented(string, expected):
    assert unaccented(string) == expected
