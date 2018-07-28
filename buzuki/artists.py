import re
from collections import Counter

from buzuki import cache
from buzuki.songs import Song
from buzuki.utils import unaccented


class Artist:
    def __init__(self, slug, num=None):
        self.slug = slug
        self.songs = [song for song in Song.all() if song.artist_slug == slug]
        self.name = self.songs[0].artist
        self.num = num or len(self.songs)

    def __repr__(self):
        return '<Artist %r>' % self.slug

    @classmethod
    @cache.memoize(timeout=60)
    def all(cls):
        artists = [song.artist_slug for song in Song.all()]
        count = Counter(artists)
        artists = [cls(slug=artist, num=count[artist]) for artist in count]
        artists.sort(key=lambda artist: unaccented(artist.name.split()[-1]))
        return artists

    @classmethod
    def search(cls, query):
        query = unaccented(query.strip())
        slug_query = re.sub(r'\s+', '_', query)
        for artist in cls.all():
            if query in unaccented(artist.name) or slug_query in artist.slug:
                yield artist
