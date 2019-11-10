from datetime import datetime, timedelta

from flask import current_app as app

from buzuki.sessions import Session


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
