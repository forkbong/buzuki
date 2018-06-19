import json

import pytest
from flask import url_for

from buzuki.songs import Song


@pytest.fixture(scope='function')
def db():
    song1 = Song(name='name_a', artist='artist', link='link', body='D#')
    song2 = Song(name='name_b', artist='artist', link='link', body='Eb')
    song1.tofile()
    song2.tofile()


def test_api_index(client, db):
    resp = client.get(url_for('api.index'))
    assert resp.status_code == 200
    assert resp.mimetype == 'application/json'
    assert len(json.loads(resp.data)) == 2


def test_api_song(client, db):
    resp = client.get(url_for('api.song', slug='name_a'))
    assert resp.status_code == 200
    assert resp.mimetype == 'application/json'
    assert resp.data.decode('unicode-escape') == (
        '{"artist":"artist"'
        ',"info":"D♯"'
        ',"link":"link"'
        ',"name":"name_a"}\n'
    )


def test_api_song_404(client):
    resp = client.get(url_for('api.song', slug='piou'))
    assert resp.status_code == 404
    assert resp.mimetype == 'application/json'
    assert resp.data == b'{}\n'


def test_api_scale(client):
    resp = client.get(url_for('api.scale', slug='xitzaz'))
    assert resp.status_code == 200
    assert resp.mimetype == 'application/json'
    assert 'Χιτζάζ'.encode('unicode_escape') in resp.data


def test_api_scale_invalid_root(client):
    resp = client.get(url_for('api.scale', slug='xitzaz', root='Z'))
    assert resp.status_code == 400
    assert resp.mimetype == 'application/json'
    assert resp.data == b'{"message":"\'Z\' is not a valid note"}\n'


def test_api_scale_404(client):
    resp = client.get(url_for('api.scale', slug='piou'))
    assert resp.status_code == 404
    assert resp.mimetype == 'application/json'
    assert resp.data == b'{}\n'


def test_api_404(client):
    for url in {'/api/asdf', '/api/asdf/'}:
        resp = client.get(url)
        assert resp.status_code == 404
        assert resp.mimetype == 'application/json'
        assert resp.data == b'{}\n'


def test_api_405(client):
    resp = client.post('/api/')
    assert resp.status_code == 405
    assert resp.mimetype == 'application/json'
    assert resp.data == \
        b'{"message":"The method is not allowed for the requested URL"}\n'
