#!/usr/bin/env python3

import json
import re
import subprocess
import sys
from multiprocessing import cpu_count
from pathlib import Path
from string import printable

import click
import IPython
import requests
import youtube_dl
from flask import current_app as app
from flask.cli import FlaskGroup, with_appcontext
from gunicorn.app.base import BaseApplication
from IPython.terminal.ipapp import load_default_config
from mutagen.id3 import COMM, ID3
from pygments import formatters, highlight, lexers
from werkzeug.security import generate_password_hash

from buzuki import DoesNotExist, cache_utils, create_app, elastic
from buzuki.artists import Artist
from buzuki.elastic import es
from buzuki.playlists import Playlist
from buzuki.scales import Scale
from buzuki.songs import Song
from buzuki.utils import FLATS, SHARPS, unaccented


def pprint(obj):
    """Pretty-print `obj` using `json` and `pygments`."""
    formatted = highlight(
        json.dumps(obj, indent=4, ensure_ascii=False),
        lexers.JsonLexer(),
        formatters.TerminalFormatter(),
    )
    print(formatted)


@click.group(cls=FlaskGroup, create_app=lambda: create_app('default'))
def cli():
    """Management script for buzuki."""


@cli.command(context_settings=dict(ignore_unknown_options=True))
@click.argument('ipython_args', nargs=-1, type=click.UNPROCESSED)
@with_appcontext
def shell(ipython_args):
    """Run a shell in the app context.

    Runs an interactive Python shell in the context of a given Flask
    application. The application will populate the default namespace of this
    shell according to it's configuration.

    This is useful for executing small snippets of management code without
    having to manually configuring the application.
    """
    # See: https://github.com/ei-grad/flask-shell-ipython
    config = load_default_config()
    config.TerminalInteractiveShell.banner1 = (
        f"Python {sys.version} on {sys.platform}\n"
        f"IPython: {IPython.__version__}\n"
        f"App: {app.import_name} [{app.env}]\n"
        f"Instance: {app.instance_path}\n"
    )

    IPython.start_ipython(
        argv=ipython_args,
        user_ns=app.make_shell_context(),
        config=config,
    )


@cli.command()
@click.option('-w', '--workers', help="Number of workers.",
              default=2 * cpu_count() + 1)
@click.option('-h', '--host', help="The interface to bind to.",
              default='127.0.0.1')
@click.option('-p', '--port', help="The port to bind to.", default=8000)
def gunicorn(workers, host, port):
    """Run a production server with gunicorn."""

    class GunicornApplication(BaseApplication):
        def load_config(self):
            self.cfg.set('bind', f'{host}:{port}')
            self.cfg.set('workers', workers)

        def load(self):
            return create_app(production=True)

    GunicornApplication().run()


@cli.command()
@click.argument('password')
def hash(password):
    """Generate password hash."""
    click.echo(generate_password_hash(password))


@cli.command()
def filenames():
    """Check that song filenames and slugs match."""
    directory: Path = app.config['DIR'] / 'songs'
    assert directory.is_dir()
    path: Path
    for path in directory.iterdir():
        song = Song.fromfile(path.name)
        if path.name != song.slug:
            if click.confirm(f"{path.name} -> {song.slug}?"):
                new_path = directory / song.slug
                path.rename(new_path)


@cli.command()
def index():
    """Index all data into elasticsearch."""
    elastic.create_index()

    def index_all(model, name):
        with click.progressbar(model.all(), label=f"Indexing {name}") as bar:
            for item in bar:
                elastic.index(item)

    index_all(Song, 'songs')
    index_all(Artist, 'artists')
    index_all(Scale, 'scales')


@cli.command()
@click.argument('query')
@click.option('-a', '--artists', is_flag=True, help="Only search for artists.")
@click.option('-v', '--verbose', is_flag=True, help="Print whole documents.")
def search(query, artists, verbose):
    """Perform a search in elasticsearch."""
    result = elastic.search(query, ['url:artists'] if artists else [])
    hits = result['hits']['hits']
    if verbose:
        pprint(hits)
    else:
        for hit in result['hits']['hits']:
            print(f"{hit['_source']['name']} ({hit['_score']})")


@cli.command()
@click.argument('query')
def analyze(query):
    """Analyze query and print tokens.

    ASCII queries are analyzed with the 'standard' and 'slug' analyzers, and
    greek queries with 'standard', 'greek_autocomplete', 'greek_lowercase' and
    'greek_stemmed' analyzers.
    """
    analyzers = ['standard']
    if re.match(fr'^[{printable}]*$', query):
        analyzers.append('slug')
    else:
        analyzers.extend([
            'greek_autocomplete',
            'greek_stemmed',
            'greek_lowercase',
        ])

    body = {'text': query}
    response = {}
    for analyzer in analyzers:
        body['analyzer'] = analyzer
        result = es.indices.analyze(index='documents', body=body)
        response[analyzer] = [token['token'] for token in result['tokens']]

    pprint(response)


@cli.command()
@click.option('-a', '--artists', is_flag=True, help="Print artists.")
@click.option('-s', '--songs', is_flag=True, help="Print songs.")
def cache(artists, songs):
    """Print the contents of the redis cache."""
    if not artists and not songs:
        artists = songs = True
    if artists:
        artists = cache_utils.get_artists()
        pprint(artists)
    if songs:
        songs = cache_utils.get_songs()
        pprint(songs)


@cli.command()
@click.argument('playlist_slug')
def playlist(playlist_slug):
    """Add song to playlist."""
    try:
        playlist = Playlist.get(playlist_slug)
    except DoesNotExist as e:
        sys.exit(e)

    songs = [song.slug for song in Song.all() if song not in playlist]
    try:
        song_slug = subprocess.run(
            ['fzf', '--no-sort', '--exact'],
            input='\n'.join(songs),
            universal_newlines=True,
            stdout=subprocess.PIPE,
        ).stdout.strip()
    except FileNotFoundError as e:
        sys.exit(e)

    if not song_slug:
        return

    song = Song.get(song_slug)
    # If the user selects nothing we leave the root empty, and the
    # default root is used. If he wants to explicitly set the default
    # root in case it's changed in the future, he has to select it.
    default = song.scale[0:2].strip()
    root = click.prompt(f'Root [{default}]', default='', show_default=False)
    if root and root not in SHARPS + FLATS:
        sys.exit(f'Invalid root: {root}')

    playlist.add(song_slug, root)


@cli.command()
def check():
    """Check and fix audio files."""

    def clear_metadata(filename):
        audio = ID3(filename)
        keys = list(audio.keys())
        if keys:
            for key in keys:
                audio.delall(key)
            audio.save()

    def set_comment(filename, comment):
        audio = ID3(filename)
        audio.add(COMM(encoding=3, text=comment))
        audio.save()

    def get_comment(filename):
        audio = ID3(filename)
        comments = audio.getall("COMM")
        if not comments:
            return
        return comments[0].text[0]

    def download(song):
        """Download `song`'s YouTube video and convert to mp3."""
        filename = ''

        def download_hook(d):
            nonlocal filename
            if d['status'] == 'finished':
                filename = d['filename']
                print("Done downloading, now converting...")

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'progress_hooks': [download_hook],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([song.link])
            except youtube_dl.DownloadError as e:
                print(click.style(
                    f"Couldn't download {song.name}: {e}", fg='bright_red'
                ))
                return

        path = Path(filename).with_suffix('.mp3')
        path.rename(song.audio_path)
        set_comment(song.audio_path, song.youtube_id)

    def check_link(song):
        """Return whether `song`'s YouTube link is still valid."""
        url = f'http://img.youtube.com/vi/{song.youtube_id}/mqdefault.jpg'
        try:
            response = requests.get(url)
        except requests.ConnectionError as e:
            sys.exit(e)
        if response.status_code != 200:
            return False
        return True

    directory: Path = app.config['DIR'] / 'songs'
    songs = [Song.get(path.name) for path in directory.iterdir()]
    songs.sort(key=lambda song: unaccented(song.name))
    num = len(songs)
    for i, song in enumerate(songs, start=1):
        print(f"{i}/{num}", end='\t')
        if song.youtube_id:
            if not check_link(song):
                assert song.audio_path.is_file()
                print(click.style(
                    f"{song.name} has invalid youtube id", fg='bright_red'
                ))
            elif song.audio_path.is_file():
                youtube_id = get_comment(song.audio_path)
                if song.youtube_id != youtube_id:
                    print(
                        f"{song.name} had changed "
                        f"({song.youtube_id} != {youtube_id})"
                    )
                    if click.confirm("Replace?"):
                        song.audio_path.unlink()
                        print(f"Downloading {song.name}...")
                        download(song)
                        print()
                else:
                    print(song.name, "is OK")
            else:
                print(f"Downloading {song.name}...")
                download(song)
                print()
        else:
            assert song.audio_path.is_file()
            print(song.name, "has no youtube id but audio is downloaded")
            clear_metadata(song.audio_path)


if __name__ == '__main__':
    cli()
