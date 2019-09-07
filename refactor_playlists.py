#!/usr/bin/env python3

from pathlib import Path

import yaml

from buzuki import create_app
from buzuki.playlists import Playlist

app = create_app('development')


def main():
    slug = 'giannis'

    playlist = Playlist.get(slug)
    songs = {}
    for song in playlist.songs:
        song_data = {
            'name': song.name,
            'artist': song.artist,
            'artist_slug': song.artist_slug,
        }
        if song.root:
            song_data['root'] = song.root

        songs[song.slug] = song_data

    playlist_data = {
        'name': playlist.name,
        'songs': songs,
    }

    data = yaml.safe_dump(playlist_data, allow_unicode=True, sort_keys=False)
    path = Path(app.config['DIR'] / 'playlists' / f'{slug}.yml')
    print(data)
    print(path)
    # path.write_text(data)


if __name__ == '__main__':
    with app.app_context():
        main()
