import os
import re
from urllib.parse import parse_qs, urlparse

from flask import current_app as app
from flask import url_for

from buzuki import DoesNotExist, cache_utils
from buzuki.mixins import Model
from buzuki.scales import Scale
from buzuki.utils import greeklish, to_unicode, transpose, transpose_to_root


class Song(Model):
    def __init__(self, name, artist, link, scale, rhythm, body):
        self.name = name
        self.artist = artist
        self.link = link
        self.scale = scale
        self.rhythm = rhythm
        self.body = body

    def __eq__(self, other):
        """Test instance equality by comparing slugs."""
        if isinstance(other, Song):
            return self.slug == other.slug
        return False

    @classmethod
    def get(cls, slug, semitones=None, root=None, unicode=False):
        """Load a song from file and optionally transpose it.

        Args:
            slug: The song's slug.
            semitones: Transpose song by given semitones.
            root: Transpose song to the given root.
            unicode: Use unicode sharps and flats in the song's body.
        """
        song = cls.fromfile(filename=slug)
        if semitones is not None:
            song.scale = transpose(song.scale, semitones)
            song.body = transpose(song.body, semitones)
        elif root is not None:
            root = re.sub('s', '#', root)
            old_root = song.scale[0:2].strip()
            song.scale = transpose_to_root(song.scale, old_root, root)
            song.body = transpose_to_root(song.body, old_root, root)
        if unicode:
            song.scale = to_unicode(song.scale)
            song.body = to_unicode(song.body)

        return song

    @classmethod
    def fromfile(cls, filename):
        directory = app.config['SONGDIR']
        path = os.path.join(directory, filename)
        try:
            with open(path) as f:
                file = f.read()
        except FileNotFoundError:
            raise DoesNotExist(f"Song '{filename}' does not exist")
        name, artist, link, rest = [x for x in file.split('\n', 3)]
        scale, rhythm, body = rest.strip('\n').split('\n\n', 2)
        song = cls(name, artist, link, scale, rhythm, body)
        return song

    @classmethod
    def frommetadata(cls, song):
        return cls(
            name=song.get('name'),
            artist=song.get('artist'),
            link=None,
            scale=song.get('scale'),
            rhythm=None,
            body=None,
        )

    @classmethod
    def all(cls):
        """Get all songs from the database."""
        songs = cache_utils.get_songs().values()
        return [cls.frommetadata(song) for song in songs]

    @property
    def youtube_id(self):
        """Extract youtube video id from url."""
        # https://gist.github.com/kmonsoor/2a1afba4ee127cce50a0
        url = self.link
        if not url.startswith('http'):
            url = 'http://' + url

        query = urlparse(url)
        if query.hostname is None:
            return None

        if 'youtube' in query.hostname:
            if query.path == '/watch':
                return parse_qs(query.query)['v'][0]
            elif query.path.startswith(('/embed/', '/v/')):
                return query.path.split('/')[2]
            else:
                return None
        elif 'youtu.be' in query.hostname:
            return query.path[1:]
        else:
            return None

    def info(self, html=False):
        """Return all song information joined into a string.

        Args:
            html: Wrap scales in links to the scale page.
        """
        _scale = self.scale

        if html:
            root = _scale[0:2].strip()
            root = re.sub('[#♯]', 's', root)
            for scale in Scale.all():
                if scale.name in _scale:
                    url = url_for('main.scale', slug=scale.slug, root=root)
                    href = f'<a href="{url}">{scale.name}</a>'
                    _scale = _scale.replace(scale.name, href)

        return '\n\n'.join([_scale, self.rhythm, self._body])

    @property
    def body(self):
        """Body getter."""
        return self._body

    @body.setter
    def body(self, value):
        """No trailing witespace and unix end-of-line characters."""
        if value is None:
            self._body = None
        else:
            body = value.strip('\n').replace('\r\n', '\n')
            body = [line.rstrip() for line in body.split('\n')]
            self._body = '\n'.join(body)

    @property
    def slug(self):
        return greeklish(self.name)

    @property
    def artist_slug(self):
        return greeklish(self.artist)

    def tofile(self):
        directory = app.config['SONGDIR']
        os.makedirs(directory, mode=0o755, exist_ok=True)
        path = os.path.join(directory, self.slug)
        with open(path, 'w') as f:
            content = [self.name, self.artist, self.link, '', self.info(), '']
            f.write('\n'.join(content))
        cache_utils.clear()

    def delete(self):
        directory = app.config['SONGDIR']
        path = os.path.join(directory, self.slug)
        os.remove(path)
        cache_utils.clear()

    @staticmethod
    def delete_all():
        directory = app.config['SONGDIR']
        if not os.path.isdir(directory):
            return
        for file in os.scandir(directory):
            os.remove(file.path)
        cache_utils.clear()
