import json
import re
from secrets import choice

from flask import (Blueprint, abort, redirect, render_template, request,
                   session, url_for)

from buzuki.artists import get_artists
from buzuki.decorators import add_slug_to_cookie
from buzuki.songs import Song
from buzuki.utils import transpose, transpose_to_root, unaccented

main = Blueprint('main', __name__)


def prepare_song(slug, semitones=None, root=None):
    """Transpose song and use unicode signs."""
    song = Song.fromfile(slug)
    if semitones is not None:
        song.body = transpose(song.body, semitones)
    elif root is not None:
        root = re.sub('s', '#', root)
        song.body = transpose_to_root(song.body, root)
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
        title='Τραγούδια',
        songs=Song.all(),
        admin=session.get('logged_in'),
    )


@main.route('/songs/<slug>/')
@main.route('/songs/<slug>/<int:semitones>')
@main.route('/songs/<slug>/<root>')
@add_slug_to_cookie
def song(slug, semitones=None, root=None):
    """A song optionally transposed by given semitones."""
    song = prepare_song(slug, semitones, root)
    return render_template(
        'song.html',
        song=song,
        semitones=semitones,
        root=root,
        admin=session.get('logged_in'),
    )


@main.route('/songs/<slug>/print')
@main.route('/songs/<slug>/<int:semitones>/print')
@main.route('/songs/<slug>/<root>/print')
def songprint(slug, semitones=None, root=None):
    """A song in a printable form."""
    song = prepare_song(slug, semitones, root)
    return render_template('songprint.html', song=song)


@main.route('/random/')
def random():
    """Redirect to a random song.

    The last accessed songs, which are located in the 'latest_songs' cookie,
    via the `add_slug_to_cookie` decorator, are excluded from the selection.
    """
    cookie = request.cookies.get('latest_songs')
    latest_songs = json.loads(cookie) if cookie else []
    song = choice([
        song for song in Song.all() if song.slug not in latest_songs
    ])
    return redirect(url_for('main.song', slug=song.slug))


@main.route('/artists/')
def artists():
    """A list of all artists in the database."""
    return render_template(
        'artists.html',
        title='Καλλιτέχνες',
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
        title=songs[0].artist,
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
             if unaccented(query) in unaccented(song.name)]

    if len(songs) > 1:
        return render_template(
            'index.html',
            title=query,
            songs=songs,
            admin=session.get('logged_in'),
        )

    if len(songs) == 1:
        return redirect(url_for('main.song', slug=songs[0].slug))

    artists = [artist for artist in get_artists()
               if unaccented(query) in unaccented(artist['name'])]

    if len(artists) > 1:
        return render_template(
            'artists.html',
            title=query,
            artists=artists,
            admin=session.get('logged_in'),
        )

    if len(artists) == 1:
        return redirect(url_for('main.artist', slug=artists[0]['slug']))

    abort(404)


@main.app_errorhandler(404)
def page_not_found(e):
    """Error 404 handler."""
    return render_template('404.html'), 404
