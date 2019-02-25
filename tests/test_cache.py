from buzuki import cache_utils
from tests.factories import SongFactory


def test_cache(client):
    SongFactory(artist='Βαμβακάρης', name='Ένα').tofile()
    SongFactory(artist='Βαμβακάρης', name='Δύο').tofile()
    SongFactory(artist='Σκαρβέλης', name='Τρία').tofile()

    assert cache_utils.get_songs() == {
        'dyo': {
            'artist': 'Βαμβακάρης',
            'artist_slug': 'vamvakaris',
            'name': 'Δύο',
            'scale': 'scale',
        },
        'ena': {
            'artist': 'Βαμβακάρης',
            'artist_slug': 'vamvakaris',
            'name': 'Ένα',
            'scale': 'scale',
        },
        'tria': {
            'artist': 'Σκαρβέλης',
            'artist_slug': 'skarvelis',
            'name': 'Τρία',
            'scale': 'scale',
        },
    }

    assert cache_utils.get_artists() == {
        'vamvakaris': {
            'name': 'Βαμβακάρης',
            'songs': [{
                'name': 'Δύο',
                'slug': 'dyo',
            }, {
                'name': 'Ένα',
                'slug': 'ena',
            }],
        },
        'skarvelis': {
            'name': 'Σκαρβέλης',
            'songs': [{
                'name': 'Τρία',
                'slug': 'tria',
            }],
        }
    }
