#!/usr/bin/env python3

import json
import os
import re
import subprocess
import sys
from multiprocessing import cpu_count
from string import printable

import click
import IPython
from flask import current_app as app
from flask.cli import FlaskGroup, with_appcontext
from gunicorn.app.base import BaseApplication
from gunicorn.config import Config as GunicornConfig
from IPython.terminal.ipapp import load_default_config
from pygments import formatters, highlight, lexers
from werkzeug.security import generate_password_hash

from buzuki import cache_utils, create_app, elastic
from buzuki.artists import Artist
from buzuki.elastic import es
from buzuki.scales import Scale
from buzuki.songs import Song


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
        f"App: {app.import_name}{' [debug]' if app.debug else ''}\n"
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
            assert isinstance(self.cfg, GunicornConfig)
            self.cfg.set('bind', f'{host}:{port}')
            self.cfg.set('workers', workers)

        def load(self):
            return create_app()

    GunicornApplication().run()


@cli.command()
@click.option('-o', '--output', help="Target directory.", default='videos')
def download(output):
    """Download all youtube videos."""

    def should_download(song):
        """Return whether the song's video needs to be downloaded."""
        for file in os.listdir(output):
            base, extension = os.path.splitext(file)
            if base == f'{song.slug}_{song.youtube_id}':
                return False
        return True

    songs = Song.all()

    with click.progressbar(
        [song for song in songs if should_download(song)],
        label="Downloading video files",
        item_show_func=lambda item: getattr(item, 'name', ''),
    ) as bar:
        for song in bar:
            subprocess.run([
                'youtube-dl',
                '--quiet',
                '--no-warnings',
                '--output',
                os.path.join(output, f'{song.slug}_{song.youtube_id}'),
                song.link,
            ])

    for file in os.listdir(output):
        base, extension = os.path.splitext(file)
        if not any(base == f'{song.slug}_{song.youtube_id}' for song in songs):
            if click.confirm(f"{file} does not match any song. Delete?"):
                os.unlink(os.path.join(output, file))


@cli.command()
@click.argument('password')
def hash(password):
    """Generate password hash."""
    click.echo(generate_password_hash(password))


@cli.command()
def filenames():
    """Check that song filenames and slugs match."""
    directory = app.config['SONGDIR']
    assert os.path.isdir(directory)
    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)
        song = Song.fromfile(path)
        if filename != song.slug:
            if click.confirm(f"{filename} -> {song.slug}?"):
                new_path = os.path.join(directory, song.slug)
                os.rename(path, new_path)


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


if __name__ == '__main__':
    cli()
