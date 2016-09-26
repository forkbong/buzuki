import os
from urllib.parse import parse_qs, urlparse

from flask import current_app as app
from sqlalchemy.ext.hybrid import hybrid_property

from buzuki import db
from buzuki.utils import greeklish


class Song(db.Model):
    __tablename__ = 'songs'

    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(64), unique=True)
    slug = db.Column(db.String(64), unique=True)
    artist = db.Column(db.String(64))
    _body = db.Column(db.Text)
    link = db.Column(db.String(64))

    def __repr__(self):
        return '<Song %r>' % greeklish(self.name)

    @classmethod
    def fromfile(cls, filename):
        directory = app.config['SONGDIR']
        path = os.path.join(directory, filename)
        with open(path) as f:
            file = f.read()
        name, artist, link, body = [x for x in file.split('\n', 3)]
        return cls(name=name, artist=artist, link=link, body=body.strip('\n'))

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

    @hybrid_property
    def name(self):
        """Name getter."""
        return self._name

    @name.setter
    def name(self, value):
        """When setting name also set slug."""
        self._name = value
        self.slug = greeklish(value, sep='_')

    @hybrid_property
    def body(self):
        """Body getter."""
        return self._body

    @body.setter
    def body(self, value):
        """No trailing witespace and unix end-of-line characters."""
        body = value.replace('\r\n', '\n')
        body = [line.rstrip() for line in body.split('\n')]
        self._body = '\n'.join(body)

    def tofile(self):
        directory = app.config['SONGDIR']
        os.makedirs(directory, mode=0o755, exist_ok=True)
        path = os.path.join(directory, self.slug)
        with open(path, 'w') as f:
            content = [self.name, self.artist, self.link, '', self.body, '']
            f.write('\n'.join(content))
