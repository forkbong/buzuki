from flask import url_for

from buzuki.songs import Song


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
            follow_redirects=True,
        )
        assert resp.status_code == 200
        with client.session_transaction() as session:
            assert session['logged_in']
        resp = client.get(url_for('admin.login'), follow_redirects=True)
        assert 'Έχεις ήδη συνδεθεί'.encode() in resp.data

    def test_redirect_and_login(self, client):
        resp = client.get(url_for('admin.index'))
        assert resp.status_code == 302
        resp = client.get(url_for('admin.index'), follow_redirects=True)
        assert resp.status_code == 200
        assert 'Συνδέσου για να συνεχίσεις'.encode() in resp.data
        with client.session_transaction() as session:
            assert session['next_url'] == url_for('admin.index')
        resp = client.post(
            url_for('admin.login'),
            data={'password': 'admin'},
            follow_redirects=True,
        )
        with client.session_transaction() as session:
            assert 'next_url' not in session
        assert b'Admin panel' in resp.data

    def test_wrong_password(self, client):
        resp = client.post(
            url_for('admin.login'),
            data={'password': 'wrong password'},
            follow_redirects=True,
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
            'link': 'link',
        },
        follow_redirects=True
    )
    song = Song.fromfile('name')
    assert song.name == 'name'


def test_save_delete(client):
    with client.session_transaction() as session:
        session['logged_in'] = True
    song = Song(name='name', artist='artist', link='link', body='Bm F# Bm')
    song.tofile()
    assert len(Song.all()) == 1
    url = url_for('admin.save', slug='name', semitones=1)
    resp = client.get(url, follow_redirects=True)
    assert resp.status_code == 200
    song = Song.fromfile('name')
    assert song.body == 'Cm G  Cm'
    resp = client.get(url_for('admin.delete', slug='name'),
                      follow_redirects=True)
    assert Song.all() == []
    resp = client.get(url_for('admin.delete', slug='name'),
                      follow_redirects=True)
    assert 'Δεν υπάρχει τέτοια σελίδα'.encode() in resp.data
