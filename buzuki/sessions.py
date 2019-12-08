from datetime import datetime, timedelta
from pathlib import Path

import yaml
from flask import current_app as app
from flask import request, session

from buzuki.songs import Song


class Session:
    def __init__(self, session_id=None):
        dirname = 'sessions-local' if app.config['DEBUG'] else 'sessions'
        self.directory: Path = app.config['DIR'] / dirname
        self.directory.mkdir(mode=0o755, exist_ok=True)
        self.session_id = session_id or self.get_session_id()
        self.path = self.directory / self.session_id
        self.songs = self.read()

    def __repr__(self):
        return f"<{self.__class__.__name__} '{self.session_id}'>"

    def __contains__(self, item):
        if isinstance(item, Song):
            return item.slug in (song['slug'] for song in self.songs)
        elif isinstance(item, str):
            return item in (song['slug'] for song in self.songs)
        else:
            raise TypeError(
                f"'in <session>' requires Song or string "
                f"as left operand, not {type(item)}"
            )

    @classmethod
    def get(cls):
        session_id = session.get('session_id')
        instance = cls(session_id)
        last_song = instance.last_song
        now = datetime.now()
        if last_song and now - last_song['timestamp'] > timedelta(hours=5):
            session_id = None
            instance = cls()
        if session_id is None:
            session['session_id'] = instance.session_id
        return instance

    @property
    def last_song(self):
        return self.songs[-1] if self.songs else None

    def get_session_id(self):
        today = datetime.now().date().strftime('%Y.%m.%d')
        files = sorted(self.directory.glob(f'{today}-*'), reverse=True)
        if not files:
            return today + '-1'
        else:
            last_day, last_number = files[0].name.split('-')
            if last_day < today:
                return today + '-1'
            else:
                return today + f'-{int(last_number) + 1}'

    def add_song(self, slug):
        now = datetime.now().replace(microsecond=0)

        write = False
        last_song = self.last_song
        if last_song and now - last_song['timestamp'] < timedelta(minutes=2):
            # Didn't stay on the last song long
            # enough, so it couldn't have been played.
            del self.songs[-1]
            write = True

        try:
            playlist_slug = request.cookies.get('playlist')
        except RuntimeError:
            # Working outside of request context
            playlist_slug = None

        if not self.songs or self.last_song['slug'] != slug:
            self.songs.append({
                'slug': slug,
                'timestamp': now,
                'playlist': playlist_slug,
            })
            write = True

        if write:
            self.write()

    def read(self):
        try:
            return yaml.safe_load(self.path.read_text()) or []
        except FileNotFoundError:
            return []

    def write(self):
        self.path.write_text(
            yaml.safe_dump(self.songs, allow_unicode=True, sort_keys=False)
        )
