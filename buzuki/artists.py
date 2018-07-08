import re
from collections import Counter

from buzuki import cache
from buzuki.songs import Song
from buzuki.utils import greeklish, unaccented


@cache.memoize(timeout=60)
def get_artists():
    """Return a list of all artists.

    Each artist is a dict with the artist's name in greek and greeklish, and
    the number of songs by him in the database.
    """
    artists = [song.artist for song in Song.all()]
    count = Counter(artists)
    artists = [{
        'name': artist,
        'slug': greeklish(artist),
        'num': count[artist]
    } for artist in count]
    # Sort and ignore accents
    artists.sort(key=lambda artist: unaccented(artist['name'].split()[-1]))
    return artists


def search_artists(query):
    query = unaccented(query.strip())
    slug_query = re.sub(r'\s+', '_', query)
    for artist in get_artists():
        if query in unaccented(artist['name']) or slug_query in artist['slug']:
            yield artist
