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


def test_artist_404(client):
    SongFactory(name='name_a').tofile()
    url = url_for('main.artist', slug='asdf')
    resp = client.get(url)
    assert resp.status_code == 404


def test_artist_one_song(client):
    SongFactory(name='name_a').tofile()
    url = url_for('main.artist', slug='artist')
    resp = client.get(url)
    assert resp.status_code == 302
    assert resp.location == url_for('main.song', slug='name_a')


def test_artist_normal(client):
    SongFactory(name='name_a').tofile()
    SongFactory(name='name_b').tofile()
    url = url_for('main.artist', slug='artist')
    resp = client.get(url)
    assert resp.status_code == 200
    assert b'name_a' in resp.data
    assert b'name_b' in resp.data
