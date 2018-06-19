from flask import url_for

from buzuki.songs import Song


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
    assert Song.get('name_a', unicode=True).body == 'D♯'
    assert Song.get('name_b', unicode=True).body == 'E♭'
    assert Song.get('name_a', semitones=-2).body == 'C#'
    assert Song.get('name_b', semitones=-2).body == 'Db'
    assert Song.get('name_a', root='B').body == 'B'
    assert Song.get('name_b', root='B').body == 'B'
