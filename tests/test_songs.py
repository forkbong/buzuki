from pathlib import Path

import pytest
from flask import current_app as app

from buzuki.songs import Song
from tests.factories import SongFactory


def test_repr(client):
    assert repr(SongFactory(name='Καλησπέρα')) == "<Song 'kalispera'>"


def test_eq(client):
    assert SongFactory(name='Καλησπέρα') == SongFactory(name='Καλησπέρα')
    assert SongFactory(name='Καλησπέρα') == SongFactory(name='καλησπερα')
    assert SongFactory(name='Καλησπέρα') != SongFactory(name='καλημερα')
    assert SongFactory(name='Καλησπέρα') != 12345


def test_info(client):
    body = (
        '\n'
        'asdf\r\n'
        '  asdf\n'
        '  asdf   \r\n'
        '\n'
    )
    expected = (
        'scale\n'
        '\n'
        'rhythm\n'
        '\n'
        'asdf\n'
        '  asdf\n'
        '  asdf'
    )
    song = SongFactory(body=body)
    assert song.info() == expected


@pytest.mark.parametrize('link', [
    ('http://youtu.be/_lOT2p_FCvA'),
    ('www.youtube.com/watch?v=_lOT2p_FCvA&feature=feedu'),
    ('http://www.youtube.com/embed/_lOT2p_FCvA'),
    ('http://www.youtube.com/v/_lOT2p_FCvA?version=3&amp;hl=en_US'),
    ('https://www.youtube.com/watch?v=_lOT2p_FCvA&index=6'),
    ('youtube.com/watch?v=_lOT2p_FCvA'),
])
def test_youtube_id(client, link):
    # https://gist.github.com/kmonsoor/2a1afba4ee127cce50a0
    song = SongFactory(link=link)
    assert song.youtube_id == '_lOT2p_FCvA'


@pytest.mark.parametrize('link', [
    (''),
    ('_lOT2p_FCvA'),
    ('http://google.com/_lOT2p_FCvA'),
    ('http://www.youtube.com/asdf/_lOT2p_FCvA'),
])
def test_invalid_youtube_id(client, link):
    song = SongFactory(link=link)
    assert song.youtube_id is None


def test_tofile(client):
    song = SongFactory()
    song.tofile()
    path = Path(app.config['SONGDIR']) / 'name'
    assert path.read_text() == (
        'name\n'
        'artist\n'
        'link\n'
        '\n'
        'scale\n'
        '\n'
        'rhythm\n'
        '\n'
        'body\n'
    )


def test_get(client):
    SongFactory().tofile()
    song = Song.get('name')
    assert song.name == 'name'
    assert song.artist == 'artist'
    assert song.link == 'link'
    assert song.body == 'body'
