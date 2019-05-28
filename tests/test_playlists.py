from textwrap import dedent

import pytest

from buzuki import DoesNotExist, InvalidNote
from buzuki.playlists import Playlist
from buzuki.songs import Song
from tests.factories import SongFactory

playlist_data = {
    'name': 'Λίστα',
    'songs': [{
        'name': 'Νέημ',
        'slug': 'neim',
        'artist': 'Βαμβακάρης',
        'artist_slug': 'vamvakaris',
        'root': 'A',
    }, {
        'name': 'Τεστ',
        'slug': 'test',
        'artist': 'Βαμβακάρης',
        'artist_slug': 'vamvakaris',
    }]
}


def test_init(client):
    songs = [
        Song.frommetadata(song_data) for song_data in playlist_data['songs']
    ]

    playlist = Playlist(name=playlist_data['name'], songs=songs)

    assert playlist.name == 'Λίστα'
    assert playlist.slug == 'lista'
    assert playlist.songs == songs
    assert playlist.num == 2


def test_contains(client):
    songs = [
        Song.frommetadata(song_data) for song_data in playlist_data['songs']
    ]
    playlist = Playlist(name=playlist_data['name'], songs=songs)
    playlist.tofile()

    assert 'test' in playlist
    assert SongFactory(name='Τεστ') in playlist
    assert 'asdf' not in playlist
    assert SongFactory(name='Ασδφ') not in playlist


def test_tofile(client):
    songs = [
        Song.frommetadata(song_data) for song_data in playlist_data['songs']
    ]
    playlist = Playlist(name=playlist_data['name'], songs=songs)

    playlist.tofile()

    assert (playlist.directory / f'{playlist.slug}.yml').read_text() == dedent(
        """\
        name: Λίστα
        songs:
        - name: Νέημ
          slug: neim
          artist: Βαμβακάρης
          artist_slug: vamvakaris
          root: A
        - name: Τεστ
          slug: test
          artist: Βαμβακάρης
          artist_slug: vamvakaris
        """
    )


def test_get(client):
    songs = [
        Song.frommetadata(song_data) for song_data in playlist_data['songs']
    ]
    playlist = Playlist(name=playlist_data['name'], songs=songs)
    playlist.tofile()

    playlist = Playlist.get('lista')

    assert playlist.name == 'Λίστα'
    assert playlist.slug == 'lista'
    assert playlist.songs == songs
    assert playlist.num == 2


def test_get_file_not_found(client):
    with pytest.raises(DoesNotExist):
        Playlist.get('asdf')


def test_all(client):
    songs = [
        Song.frommetadata(song_data) for song_data in playlist_data['songs']
    ]
    playlist = Playlist(name=playlist_data['name'], songs=songs)
    playlist.tofile()

    assert Playlist.all() == [playlist]


def test_add(client):
    songs = [
        Song.frommetadata(song_data) for song_data in playlist_data['songs']
    ]
    playlist = Playlist(name=playlist_data['name'], songs=songs)
    playlist.tofile()
    SongFactory(name='Ασδφ', artist='Ασδφ').tofile()

    playlist.add('asdf')

    assert (playlist.directory / f'{playlist.slug}.yml').read_text() == dedent(
        """\
        name: Λίστα
        songs:
        - name: Ασδφ
          slug: asdf
          artist: Ασδφ
          artist_slug: asdf
        - name: Νέημ
          slug: neim
          artist: Βαμβακάρης
          artist_slug: vamvakaris
          root: A
        - name: Τεστ
          slug: test
          artist: Βαμβακάρης
          artist_slug: vamvakaris
        """
    )


def test_add_invalid_root(client):
    songs = [
        Song.frommetadata(song_data) for song_data in playlist_data['songs']
    ]
    playlist = Playlist(name=playlist_data['name'], songs=songs)
    playlist.tofile()
    SongFactory(name='Ασδφ', artist='Ασδφ').tofile()

    with pytest.raises(InvalidNote):
        playlist.add('asdf', root='L')


def test_remove(client):
    songs = [
        Song.frommetadata(song_data) for song_data in playlist_data['songs']
    ]
    playlist = Playlist(name=playlist_data['name'], songs=songs)
    playlist.tofile()

    playlist.remove('neim')

    assert (playlist.directory / f'{playlist.slug}.yml').read_text() == dedent(
        """\
        name: Λίστα
        songs:
        - name: Τεστ
          slug: test
          artist: Βαμβακάρης
          artist_slug: vamvakaris
        """
    )
