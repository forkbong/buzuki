from datetime import datetime, timedelta
from pathlib import Path

from flask import current_app as app
from flask import url_for

from buzuki.sessions import Session
from tests.factories import SongFactory


def test_session(client):
    session = Session('2019.11.11-1')

    assert session.path == app.config['DIR'] / 'sessions' / '2019.11.11-1'

    session.add_song('song1')
    session_data = session.read()

    assert len(session_data) == 1
    assert session_data[0]['slug'] == 'song1'
    assert 'song1' in session
    assert 'song2' not in session
    assert 'song3' not in session

    session.add_song('song2')
    session_data = session.read()

    assert len(session_data) == 1
    assert session_data[0]['slug'] == 'song2'
    assert 'song1' not in session
    assert 'song2' in session
    assert 'song3' not in session

    timestamp = datetime.now().replace(microsecond=0) - timedelta(minutes=3)
    session.songs[0]['timestamp'] = timestamp
    session.write()
    session.add_song('song3')
    session_data = session.read()

    assert len(session_data) == 2
    assert session_data[0]['slug'] == 'song2'
    assert session_data[1]['slug'] == 'song3'
    assert 'song1' not in session
    assert 'song2' in session
    assert 'song3' in session


def test_session_get(client):
    SongFactory(name='name').tofile()
    url = url_for('main.song', slug='name')

    today = datetime.now().date().strftime('%Y.%m.%d')
    session_id = f'{today}-1'
    filename: Path = app.config['DIR'] / 'sessions' / session_id

    resp = client.get(url)
    assert resp.status_code == 200
    assert not filename.is_file()

    client.post(
        url_for('admin.login'),
        data={'password': 'admin'},
        follow_redirects=True,
    )

    resp = client.get(url)
    assert resp.status_code == 200
    assert filename.is_file()

    session = Session(session_id)
    assert len(session.songs) == 1
    assert session.songs[0]['slug'] == 'name'
    assert 'name' in session
