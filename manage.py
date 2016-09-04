#!/usr/bin/env python3

import os

import click
from flask import current_app
from flask.cli import FlaskGroup

from buzuki import create_app, db
from buzuki.models import Song
from buzuki.utils import export_song


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
        export_song(song, directory)


@cli.command('import')
@click.option('-d', '--directory', help="song directory")
def import_songs(directory):
    """Import songs to the database."""
    print("Importing...")
    Song.query.delete()
    directory = directory or current_app.config['SONGDIR']
    files = os.listdir(directory)
    for name in files:
        path = os.path.join(directory, name)
        with open(path) as f:
            file = f.read()
        name, artist, link, body = [x for x in file.split('\n', 3)]
        song = Song(name=name, artist=artist, link=link, body=body.strip('\n'))
        db.session.add(song)
    db.session.commit()


if __name__ == '__main__':
    cli()
