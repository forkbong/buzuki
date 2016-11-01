from collections import Counter

from buzuki.songs import Song
from buzuki.utils import greeklish


def get_artists():
    """Return a list of all artists.

    Each artist is a dict with the artist's name in greek and greeklish, and
    the number of songs by him in the database.
    """
    artists = [song.artist for song in Song.all()]
    count = Counter(artists)
    return [{
        'name': artist,
        'slug': greeklish(artist, sep='_'),
        'num': count[artist]
    } for artist in count]
