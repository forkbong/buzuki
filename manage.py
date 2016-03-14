#!/usr/bin/env python3

import os

from flask import current_app
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell
from flask_script.commands import ShowUrls

from buzuki import create_app, db
from buzuki.models import Song
from buzuki.utils import export_song


def make_shell_context():
    return dict(app=app, db=db, Song=Song)


app = create_app()
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)
manager.add_command('urls', ShowUrls)


@MigrateCommand.option('--directory', '-d', dest='directory',
                       help="song directory")
def exportsongs(directory):
    """Export songs from the database."""
    print("Exporting...")
    songs = Song.query.all()
    for song in songs:
        export_song(song, directory)


@MigrateCommand.option('--directory', '-d', dest='directory',
                       help="song directory")
def importsongs(directory):
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
    manager.run()
