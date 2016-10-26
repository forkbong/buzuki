import pytest

from buzuki.models import Song


@pytest.mark.parametrize('name, expected_repr, expected_slug', [
    ('ασδφ', 'asdf', 'asdf'),
    ('τεστ τεστ', 'test test', 'test_test'),
    ('Τουτ\' οι μπάτσοι', 'tout oi mpatsoi', 'tout_oi_mpatsoi'),
    ('Γιατί φουμάρω κοκαΐνη', 'giati foumaro kokaini',
     'giati_foumaro_kokaini'),
])
def test_repr_slug(client, name, expected_repr, expected_slug):
    song = Song(name=name, artist='artist', link='link', body='body')
    assert repr(song) == '<Song \'{}\'>'.format(expected_repr)
    assert song.slug == expected_slug


@pytest.mark.parametrize('body, expected', [
    ('asdf  \r\n  asdf  \r\n', 'asdf\n  asdf\n'),
    ('asdf\nasdf\n', 'asdf\nasdf\n'),
])
def test_body(client, body, expected):
    song = Song(name='name', artist='artist', link='link', body=body)
    assert song.body == expected


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
    song = Song(name='name', artist='artist', link=link, body='body')
    assert song.youtube_id == '_lOT2p_FCvA'


@pytest.mark.parametrize('link', [
    (''),
    ('_lOT2p_FCvA'),
    ('http://google.com/_lOT2p_FCvA'),
    ('http://www.youtube.com/asdf/_lOT2p_FCvA'),
])
def test_invalid_youtube_id(client, link):
    song = Song(name='name', artist='artist', link=link, body='body')
    assert song.youtube_id is None


def test_database(client):
    song = Song(name='name', artist='artist', link='link', body='body')
    song.tofile()
    song = Song.fromfile('name')
    assert song.name == 'name'
    assert song.artist == 'artist'
    assert song.link == 'link'
    assert song.body == 'body'


def test_tofile(client):
    song = Song(name='name', artist='artist', link='link', body='body')
    song.tofile()
    with open('/tmp/buzuki_test/name') as f:
        assert f.read() == (
            'name\n'
            'artist\n'
            'link\n'
            '\n'
            'body\n'
        )


def test_fromfile(client):
    Song(name='name', artist='artist', link='link', body='body').tofile()
    song = Song.fromfile('name')
    assert song.name == 'name'
    assert song.artist == 'artist'
    assert song.link == 'link'
    assert song.body == 'body'
