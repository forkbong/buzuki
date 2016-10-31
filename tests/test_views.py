from flask import url_for

from buzuki import db
from buzuki.models import Song
from buzuki.views import prepare_song


def test_index(client):
    resp = client.get(url_for('main.index'))
    assert resp.status_code == 200


def test_redirect(client):
    resp = client.get(url_for('admin.index'))
    assert resp.status_code == 302
    resp = client.get(url_for('admin.index'), follow_redirects=True)
    assert resp.status_code == 200
    assert 'Συνδέσου για να συνεχίσεις'.encode() in resp.data
    with client.session_transaction() as session:
        assert session['next_url'] == url_for('admin.index')


def test_404(client):
    resp = client.get('/asdf')
    assert resp.status_code == 404
    assert 'Δεν υπάρχει τέτοια σελίδα'.encode() in resp.data


def test_prepare_song(client):
    song1 = Song(name='name_a', artist='artist', link='link', body='D#')
    song2 = Song(name='name_b', artist='artist', link='link', body='Eb')
    db.session.add(song1)
    db.session.add(song2)
    db.session.commit()
    assert prepare_song('name_a').body == 'D♯'
    assert prepare_song('name_b').body == 'E♭'
    assert prepare_song('name_a', semitones=-2).body == 'C♯'
    assert prepare_song('name_b', semitones=-2).body == 'D♭'


class TestLogin:
    def test_session(self, client):
        with client.session_transaction() as session:
            session['logged_in'] = True
        resp = client.get(url_for('admin.index'))
        assert resp.status_code == 200

    def test_form(self, client):
        resp = client.post(
            url_for('admin.login'),
            data={'password': 'admin'},
            follow_redirects=True
        )
        assert resp.status_code == 200
        with client.session_transaction() as session:
            assert session['logged_in']

        resp = client.get(url_for('admin.login'), follow_redirects=True)
        assert 'Έχεις ήδη συνδεθεί'.encode() in resp.data

    def test_redirect(self, client):
        client.get(url_for('admin.index'))
        with client.session_transaction() as session:
            assert session['next_url'] == url_for('admin.index')
        resp = client.post(
            url_for('admin.login'),
            data={'password': 'admin'},
            follow_redirects=True
        )
        with client.session_transaction() as session:
            assert 'next_url' not in session
        assert b'Admin panel' in resp.data

    def test_wrong_password(self, client):
        resp = client.post(
            url_for('admin.login'),
            data={'password': 'wrong password'},
            follow_redirects=True
        )
        assert resp.status_code == 200
        assert b'Incorrect password' in resp.data


def test_logout(client):
    with client.session_transaction() as session:
        session['logged_in'] = True
    client.get(url_for('admin.logout'), follow_redirects=True)
    with client.session_transaction() as session:
        assert not session['logged_in']


def test_add(client):
    with client.session_transaction() as session:
        session['logged_in'] = True
    resp = client.get(url_for('admin.add'))
    assert 'Νέο τραγούδι'.encode() in resp.data
    resp = client.post(
        url_for('admin.add'),
        data={
            'name': 'name',
            'artist': 'artist',
            'body': 'body',
            'link': 'link'
        },
        follow_redirects=True
    )
    song = Song.query.get(1)
    assert song.name == 'name'


def test_save_delete(client):
    with client.session_transaction() as session:
        session['logged_in'] = True
    song = Song(name='name', artist='artist', link='link', body='Bm F# Bm')
    db.session.add(song)
    db.session.commit()
    url = url_for('admin.save', slug='name', semitones=1)
    resp = client.get(url, follow_redirects=True)
    assert resp.status_code == 200
    song = Song.query.get(1)
    assert song.body == 'Cm G  Cm'
    resp = client.get(url_for('admin.delete', slug='name'),
                      follow_redirects=True)
    assert Song.query.all() == []
    resp = client.get(url_for('admin.delete', slug='name'),
                      follow_redirects=True)
    assert 'Δεν υπάρχει τέτοια σελίδα'.encode() in resp.data
