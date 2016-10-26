import re
import logging

from flask import Blueprint, render_template, session

from buzuki.models import Song
from buzuki.utils import transpose

main = Blueprint('main', __name__)


def prepare_song(slug, semitones=0):
    """Transpose song and use unicode signs."""
    song = Song.fromfile(slug)
    if semitones != 0:
        song.body = transpose(song.body, semitones)
    # FIXME: We assume that songs are greek
    # and there will be no 'b' in lyrics.
    song.body = re.sub('b', '♭', song.body)
    song.body = re.sub('#', '♯', song.body)
    return song


@main.route('/')
@main.route('/songs/')
def index():
    """A list of all songs in the database."""
    return render_template(
        'index.html',
        songs=Song.all(),
        admin=session.get('logged_in'),
    )


@main.route('/songs/<slug>/')
@main.route('/songs/<slug>/<int:semitones>')
def song(slug, semitones=0):
    """A song optionally transposed by given semitones."""
    song = prepare_song(slug, semitones)
    return render_template(
        'song.html',
        song=song,
        semitones=semitones,
        admin=session.get('logged_in'),
    )


@main.route('/songs/<slug>/print')
@main.route('/songs/<slug>/<int:semitones>/print')
def songprint(slug, semitones=0):
    """A song in a printable form."""
    song = prepare_song(slug, semitones)
    return render_template('songprint.html', song=song)


@main.app_errorhandler(404)
def page_not_found(e):
    """Error 404 handler."""
    logging.error(e)
    return render_template('404.html'), 404
