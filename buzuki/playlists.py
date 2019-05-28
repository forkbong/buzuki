import re
from pathlib import Path

import yaml
from flask import current_app as app

from buzuki import DoesNotExist, InvalidNote
from buzuki.mixins import Model
from buzuki.songs import Song
from buzuki.utils import unaccented


class Playlist(Model):
    def __init__(self, name, songs):
        self.name = name
        self.songs = songs
        self.num = len(songs)
        self.directory: Path = app.config['DIR'] / 'playlists'
        self.directory.mkdir(mode=0o755, exist_ok=True)

    def __contains__(self, item):
        if isinstance(item, Song):
            return item in self.songs
        elif isinstance(item, str):
            return item in (song.slug for song in self.songs)
        else:
            raise TypeError(
                f"'in <playlist>' requires Song or string "
                f"as left operand, not {type(item)}"
            )

    @classmethod
    def get(cls, slug):
        """Playlist constructor that takes the name of the scale."""
        path: Path = app.config['DIR'] / 'playlists' / f'{slug}.yml'
        try:
            data = yaml.safe_load(path.read_text())
        except FileNotFoundError:
            raise DoesNotExist(f"Playlist '{slug}' does not exist")

        return cls(
            name=data['name'],
            songs=[Song.frommetadata(song) for song in data['songs']],
        )

    @classmethod
    def all(cls):
        directory: Path = app.config['DIR'] / 'playlists'
        directory.mkdir(mode=0o755, exist_ok=True)
        return [
            cls.get(path.stem)
            for path in directory.iterdir()
            if path.suffix == '.yml'
        ]

    def get_data(self):
        playlist_data = {
            'name': self.name,
            'songs': [],
        }
        for song in self.songs:
            song_data = {
                'name': song.name,
                'slug': song.slug,
                'artist': song.artist,
                'artist_slug': song.artist_slug,
            }
            if song.root:
                song_data['root'] = song.root
            playlist_data['songs'].append(song_data)

        return playlist_data

    def tofile(self):
        playlist_data = self.get_data()
        data = yaml.safe_dump(
            playlist_data, allow_unicode=True, sort_keys=False
        )
        path = self.directory / f'{self.slug}.yml'
        path.write_text(data)

    def add(self, song_slug, root=None):
        if root and not re.match('^[A-G][bs]?$', root):
            raise InvalidNote(f"'{root}' is not a valid note")

        self.songs = [song for song in self.songs if song.slug != song_slug]
        song = Song.get(song_slug, root=root)
        self.songs.append(song)
        self.songs.sort(key=lambda song: unaccented(song.name))
        self.tofile()

    def remove(self, song_slug):
        self.songs = [song for song in self.songs if song.slug != song_slug]
        self.tofile()
