from collections import Counter

from buzuki import cache
from buzuki.mixins import Model
from buzuki.songs import Song
from buzuki.utils import unaccented


class Artist(Model):
    def __init__(self, slug, num=None):
        self.slug = slug
        self.songs = [song for song in Song.all() if song.artist_slug == slug]
        self.name = self.songs[0].artist
        self.num = num or len(self.songs)

    @classmethod
    @cache.memoize(timeout=60)
    def all(cls):
        artists = [song.artist_slug for song in Song.all()]
        count = Counter(artists)
        artists = [cls(slug=artist, num=count[artist]) for artist in count]
        artists.sort(key=lambda artist: unaccented(artist.name.split()[-1]))
        return artists

    @property
    def genitive(self):
        last_name = self.name.split()[-1]
        transformations = {
            'άς': 'ά',
            'ας': 'α',
            'ης': 'η',
            'ος': 'ου',
            'ός': 'ού',
        }
        for key, value in transformations.items():
            if last_name.endswith(key):
                return last_name.replace(key, value)
        return last_name
