from flask import url_for

from buzuki.songs import Song
from buzuki.views import prepare_song


def test_index(client):
    resp = client.get(url_for('main.index'))
    assert resp.status_code == 200


def test_404(client):
    resp = client.get('/asdf')
    assert resp.status_code == 404
    assert 'Δεν υπάρχει τέτοια σελίδα'.encode() in resp.data


def test_prepare_song(client):
    song1 = Song(name='name_a', artist='artist', link='link', body='D#')
    song2 = Song(name='name_b', artist='artist', link='link', body='Eb')
    song1.tofile()
    song2.tofile()
    assert prepare_song('name_a').body == 'D♯'
    assert prepare_song('name_b').body == 'E♭'
    assert prepare_song('name_a', semitones=-2).body == 'C♯'
    assert prepare_song('name_b', semitones=-2).body == 'D♭'
