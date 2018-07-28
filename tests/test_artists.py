from buzuki.artists import Artist
from buzuki.songs import Song


class TestArtist:
    def test_artist(self, client):
        Song(name='a', artist='artist', link='link', body='body').tofile()
        Song(name='b', artist='artist', link='link', body='body').tofile()
        assert repr(Artist('artist')) == "<Artist 'artist'>"

    def test_all(self, client):
        Song(name='a', artist='artist_a', link='link', body='body').tofile()
        Song(name='b', artist='artist_a', link='link', body='body').tofile()
        Song(name='c', artist='artist_a', link='link', body='body').tofile()
        Song(name='d', artist='artist_b', link='link', body='body').tofile()
        assert len(Artist.all()) == 2

    def test_search(self, client):
        Song(name='a', artist='lorem ipsum', link='link', body='body').tofile()
        Song(name='b', artist='lorem ipsum', link='link', body='body').tofile()
        Song(name='c', artist='lalalalalal', link='link', body='body').tofile()

        artists = list(Artist.search('ipsum'))
        assert len(artists) == 1
        assert len(artists[0].songs) == 2
        assert artists[0].slug == 'lorem_ipsum'

        artists = list(Artist.search('la'))
        assert len(artists) == 1
        assert len(artists[0].songs) == 1
        assert artists[0].slug == 'lalalalalal'
