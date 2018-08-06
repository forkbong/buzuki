from buzuki.artists import Artist
from tests.factories import SongFactory


class TestArtist:
    def test_artist(self, client):
        SongFactory(name='a').tofile()
        SongFactory(name='b').tofile()
        assert repr(Artist('artist')) == "<Artist 'artist'>"

    def test_all(self, client):
        SongFactory(name='a', artist='artist_a').tofile()
        SongFactory(name='b', artist='artist_a').tofile()
        SongFactory(name='c', artist='artist_a').tofile()
        SongFactory(name='d', artist='artist_b').tofile()
        assert len(Artist.all()) == 2

    def test_search(self, client):
        SongFactory(name='a', artist='lorem ipsum').tofile()
        SongFactory(name='b', artist='lorem ipsum').tofile()
        SongFactory(name='c', artist='lalalalalal').tofile()

        artists = list(Artist.search('ipsum'))
        assert len(artists) == 1
        assert len(artists[0].songs) == 2
        assert artists[0].slug == 'lorem_ipsum'

        artists = list(Artist.search('la'))
        assert len(artists) == 1
        assert len(artists[0].songs) == 1
        assert artists[0].slug == 'lalalalalal'
