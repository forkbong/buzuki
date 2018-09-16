#!/usr/bin/env python3

import os
import subprocess
import sys
from multiprocessing import cpu_count

import click
import IPython
from flask import current_app as app
from flask.cli import FlaskGroup, with_appcontext
from gunicorn.app.base import BaseApplication
from IPython.terminal.ipapp import load_default_config
from werkzeug.security import generate_password_hash

from buzuki import create_app
from buzuki.songs import Song


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


if __name__ == '__main__':
    cli()
