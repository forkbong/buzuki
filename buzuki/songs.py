import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from flask import current_app as app
from flask import url_for

from buzuki import DoesNotExist, cache_utils
from buzuki.mixins import Model
from buzuki.scales import Scale
from buzuki.utils import greeklish, to_unicode, transpose, transpose_to_root


class Song(Model):
    def __init__(self, name, artist, link, scale, rhythm, body, root=None):
        self.name = name
        self.artist = artist
        self.link = link
        self.scale = scale
        self.rhythm = rhythm
        self.body = body
        self.root = root
        self.directory: Path = app.config['DIR'] / 'songs'
        self.directory.mkdir(mode=0o755, exist_ok=True)

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
        assert song.body is not None
        if semitones is not None:
            song.scale = transpose(song.scale, semitones)
            song.body = transpose(song.body, semitones)
        elif root is not None:
            root = re.sub('s', '#', root)
            old_root = song.scale[0:2].strip()
            song.scale = transpose_to_root(song.scale, old_root, root)
            song.body = transpose_to_root(song.body, old_root, root)
            song.root = root
        if unicode:
            song.scale = to_unicode(song.scale)
            song.body = to_unicode(song.body)

        return song

    @classmethod
    def fromfile(cls, filename):
        path: Path = app.config['DIR'] / 'songs' / filename
        if not path.is_file():
            raise DoesNotExist(f"Song '{filename}' does not exist")
        file = path.read_text()
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
            root=song.get('root'),
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
    def artist_slug(self):
        return greeklish(self.artist)

    @property
    def playlists(self):
        from buzuki.playlists import Playlist

        playlists = []
        for playlist in Playlist.all():
            matches = [
                song for song in playlist.songs if song.slug == self.slug
            ]
            match = matches[0] if matches else None

            playlists.append({
                'name': playlist.name,
                'slug': playlist.slug,
                'member': match is not None,
                'root': match.root if match is not None else None,
            })

        return playlists

    def tofile(self):
        path: Path = self.directory / self.slug
        content = [self.name, self.artist, self.link, '', self.info(), '']
        path.write_text('\n'.join(content))
        cache_utils.clear()

    def delete(self):
        path: Path = self.directory / self.slug
        path.unlink()
        cache_utils.clear()

    @staticmethod
    def delete_all():
        directory: Path = app.config['DIR'] / 'songs'
        if not directory.is_dir():
            return
        path: Path
        for path in directory.iterdir():
            path.unlink()
        cache_utils.clear()
