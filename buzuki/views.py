import re

from flask import (Blueprint, abort, redirect, render_template, request,
                   session, url_for)

from buzuki.artists import get_artists
from buzuki.songs import Song
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


@main.route('/artists/')
def artists():
    """A list of all artists in the database."""
    return render_template(
        'artists.html',
        artists=get_artists(),
        admin=session.get('logged_in'),
    )


@main.route('/artists/<slug>/')
def artist(slug):
    """A list of all songs from given artist."""
    songs = [song for song in Song.all()
             if song.artist_slug == slug]

    if len(songs) == 1:
        return redirect(url_for('main.song', slug=songs[0].slug))

    return render_template(
        'index.html',
        songs=songs,
        admin=session.get('logged_in'),
    )


@main.route('/search/')
def search():
    query = request.args.get('q')
    if not query:
        return redirect(url_for('main.index'))

    query = query.strip()
    songs = [song for song in Song.all()
             if query.lower() in song.name.lower()]

    if len(songs) > 1:
        return render_template(
            'index.html',
            songs=songs,
            admin=session.get('logged_in'),
        )

    if len(songs) == 1:
        return redirect(url_for('main.song', slug=songs[0].slug))

    abort(404)


@main.app_errorhandler(404)
def page_not_found(e):
    """Error 404 handler."""
    return render_template('404.html'), 404
