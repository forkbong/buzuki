#!/usr/bin/env python3

import os
from multiprocessing import cpu_count

import click
from flask import current_app
from flask.cli import FlaskGroup
from gunicorn.app.base import BaseApplication
from gunicorn.config import Config as GunicornConfig

from buzuki import create_app, db
from buzuki.models import Song


@click.group(cls=FlaskGroup, create_app=lambda: create_app('default'))
def cli():
    """Management script for buzuki."""


@cli.command('export')
@click.option('-d', '--directory', help="song directory")
def export_songs(directory):
    """Export songs from the database."""
    print("Exporting...")
    songs = Song.query.all()
    for song in songs:
        song.export(directory)


@cli.command('import')
@click.option('-d', '--directory', help="song directory")
def import_songs(directory):
    """Import songs to the database."""
    print("Importing...")
    Song.query.delete()
    directory = directory or current_app.config['SONGDIR']
    for filename in os.listdir(directory):
        song = Song.fromfile(filename)
        db.session.add(song)
    db.session.commit()


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


if __name__ == '__main__':
    cli()
