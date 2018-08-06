from flask import url_for

from buzuki.songs import Song
from tests.factories import SongFactory


def test_index(client):
    resp = client.get(url_for('main.index'))
    assert resp.status_code == 200


def test_404(client):
    resp = client.get('/asdf')
    assert resp.status_code == 404
    assert 'Δεν υπάρχει τέτοια σελίδα'.encode() in resp.data


def test_prepare_song(client):
    song1 = SongFactory(name='name_a', scale='D#')
    song2 = SongFactory(name='name_b', scale='Eb')
    song1.tofile()
    song2.tofile()
    assert Song.get('name_a', unicode=True).scale == 'D♯'
    assert Song.get('name_b', unicode=True).scale == 'E♭'
    assert Song.get('name_a', semitones=-2).scale == 'C#'
    assert Song.get('name_b', semitones=-2).scale == 'Db'
    assert Song.get('name_a', root='B').scale == 'B'
    assert Song.get('name_b', root='B').scale == 'B'
