from buzuki import DoesNotExist, cache_utils
from buzuki.mixins import Model
from buzuki.songs import Song
from buzuki.utils import greeklish


class Artist(Model):
    def __init__(self, name, songs):
        self.name = name
        self.songs = songs
        self.num = len(songs)

    @classmethod
    def get(cls, slug):
        try:
            artist = cache_utils.get_artists()[slug]
        except KeyError:
            raise DoesNotExist(f"Artist '{slug}' does not exist")
        return cls.frommetadata(artist)

    @classmethod
    def frommetadata(cls, artist):
        songs = [Song.frommetadata(song) for song in artist['songs']]
        return cls(
            name=artist['name'],
            songs=songs,
        )

    @classmethod
    def all(cls):
        artists = cache_utils.get_artists().values()
        return [cls.frommetadata(artist) for artist in artists]

    @property
    def slug(self):
        return greeklish(self.name)

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
