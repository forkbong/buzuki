import os
from urllib.parse import parse_qs, urlparse

from flask import abort
from flask import current_app as app

from buzuki.utils import greeklish, unaccented


class Song:
    def __init__(self, name, artist, link, body):
        self.name = name
        self.artist = artist
        self.link = link
        self.body = body

    def __repr__(self):
        return '<Song %r>' % self.slug

    @classmethod
    def fromfile(cls, filename):
        directory = app.config['SONGDIR']
        path = os.path.join(directory, filename)
        try:
            with open(path) as f:
                file = f.read()
        except FileNotFoundError:
            abort(404)
        name, artist, link, body = [x for x in file.split('\n', 3)]
        return cls(name=name, artist=artist, link=link, body=body.strip('\n'))

    @classmethod
    def all(cls):
        """Get all songs from the database."""
        songs = []
        directory = app.config['SONGDIR']
        if not os.path.isdir(directory):
            return songs
        for filename in os.listdir(directory):
            path = os.path.join(directory, filename)
            assert os.path.isfile(path)
            song = cls.fromfile(path)
            songs.append(song)
        # Sort and ignore accents
        songs.sort(key=lambda song: unaccented(song.name))
        return songs

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

    @property
    def body(self):
        """Body getter."""
        return self._body

    @body.setter
    def body(self, value):
        """No trailing witespace and unix end-of-line characters."""
        body = value.replace('\r\n', '\n')
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
            content = [self.name, self.artist, self.link, '', self.body, '']
            f.write('\n'.join(content))

    def delete(self):
        directory = app.config['SONGDIR']
        path = os.path.join(directory, self.slug)
        os.remove(path)

    @staticmethod
    def delete_all():
        directory = app.config['SONGDIR']
        if not os.path.isdir(directory):
            return
        for file in os.scandir(directory):
            os.remove(file.path)
