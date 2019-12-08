import json
import logging
import re
from secrets import choice

from flask import Blueprint, abort
from flask import current_app as app
from flask import (redirect, render_template, request, send_from_directory,
                   session, url_for)

from buzuki.artists import Artist
from buzuki.decorators import (add_slug_to_cookie, delete_cookie,
                               login_required, set_cookie)
from buzuki.playlists import Playlist, get_selected_playlist
from buzuki.related import get_related
from buzuki.scales import Scale
from buzuki.sessions import Session
from buzuki.songs import Song

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/songs/')
@delete_cookie('playlist')
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
    playlist = get_selected_playlist()
    if playlist and not root:
        try:
            root = playlist.roots[slug]
        except KeyError:
            pass

    if session.get('logged_in') and request.args.get('random') != 'true':
        Session.get().add_song(slug)

    song = Song.get_or_404(slug, semitones=semitones, root=root, unicode=True)
    artist = Artist.get(song.artist_slug)
    related_songs = get_related(slug)
    if related_songs is not None:
        related_title = 'Σχετικά'
    else:
        related_songs = [song for song in artist.songs if song.slug != slug]
        related_title = (
            'Άλλα παραδοσιακά'
            if song.artist == 'Παραδοσιακό'
            else f'Άλλα του {artist.genitive}'
        )

    return render_template(
        'song.html',
        song=song,
        artist=artist,
        songs=related_songs,
        related_title=related_title,
        semitones=semitones,
        root=root,
        admin=session.get('logged_in'),
    )


@main.route('/songs/<slug>/print')
@main.route('/songs/<slug>/<int:semitones>/print')
@main.route('/songs/<slug>/<root>/print')
def songprint(slug, semitones=None, root=None):
    """A song in a printable form."""
    song = Song.get_or_404(slug, semitones=semitones, root=root, unicode=True)
    return render_template('songprint.html', song=song)


@main.route('/random/')
def random():
    """Redirect to a random song.

    The song is chosen randomly from the selected playlist, or the whole
    database, if no playlist is selected.

    The last accessed songs, which are located in the 'latest_songs' cookie,
    via the `add_slug_to_cookie` decorator, are excluded from the selection.
    """
    playlist_slug = request.cookies.get('playlist')
    songs = Playlist.get(playlist_slug).songs if playlist_slug else Song.all()
    cookie = request.cookies.get('latest_songs')
    latest_songs = json.loads(cookie) if cookie else []
    song = choice([song for song in songs if song.slug not in latest_songs])
    return redirect(url_for('main.song', slug=song.slug) + '?random=true')


@main.route('/artists/')
def artists():
    """A list of all artists in the database."""
    return render_template(
        'list.html',
        title='Καλλιτέχνες',
        objects=Artist.all(),
        detail_url='main.artist',
        admin=session.get('logged_in'),
    )


@main.route('/artists/<slug>/')
def artist(slug):
    """A list of all songs from given artist."""
    artist = Artist.get_or_404(slug)

    if artist.num == 1:
        return redirect(url_for('main.song', slug=artist.songs[0].slug))

    return render_template(
        'index.html',
        title=artist.name,
        songs=artist.songs,
        admin=session.get('logged_in'),
        artist=True,
    )


@main.route('/scales/')
def scales():
    """The scale's notes and a list of all songs in that scale."""
    return render_template(
        'scales.html',
        scales=Scale.all(),
        admin=session.get('logged_in'),
    )


@main.route('/scales/<slug>/')
@main.route('/scales/<slug>/<root>')
def scale(slug, root='D'):
    """A list of all available scales."""
    if not re.match('^[A-G][bs]?$', root):
        abort(404)
    root = re.sub('s', '#', root)
    scale = Scale.get_or_404(slug)
    scale.root = root
    songs = [song for song in Song.all() if scale.name in song.scale]
    scales = [s for s in Scale.all() if s.slug != scale.slug]
    return render_template(
        'scale.html',
        scale=scale,
        songs=songs,
        scales=scales,
        admin=session.get('logged_in'),
    )


@main.route('/playlists/')
@login_required
def playlists():
    """A list of all playlists in the database."""
    return render_template(
        'list.html',
        title='Λίστες',
        objects=Playlist.all(),
        detail_url='main.playlist',
        admin=session.get('logged_in'),
    )


@main.route('/playlists/<slug>/')
@login_required
@set_cookie('playlist', 'slug')
def playlist(slug):
    """A list of all songs in a given playlist."""
    playlist = Playlist.get_or_404(slug)
    return render_template(
        'index.html',
        title=playlist.name,
        songs=playlist.songs,
        admin=session.get('logged_in'),
    )


@main.route('/complement/<slug>/')
@login_required
def complement(slug):
    """A list of all songs in a given playlist."""
    playlist = Playlist.get_or_404(slug)
    all_songs = Song.all()
    songs = [song for song in all_songs if song not in playlist.songs]
    return render_template(
        'index.html',
        title=playlist.name,
        songs=songs,
        admin=session.get('logged_in'),
    )


@main.route('/search/')
def search():
    query = request.args.get('q')
    if not query:
        return redirect(url_for('main.index'))

    songs = list(Song.search(query))

    if len(songs) > 1:
        return render_template(
            'index.html',
            title=query,
            songs=songs,
            admin=session.get('logged_in'),
        )

    if len(songs) == 1:
        return redirect(url_for('main.song', slug=songs[0].slug))

    artists = list(Artist.search(query))

    if len(artists) > 1:
        return render_template(
            'list.html',
            title=query,
            objects=artists,
            detail_url='main.artist',
            admin=session.get('logged_in'),
        )

    if len(artists) == 1:
        return redirect(url_for('main.artist', slug=artists[0].slug))

    if any(scale.name == query for scale in Scale.all()):
        scale = Scale.get(query)
        return redirect(url_for('main.scale', slug=scale.slug))

    abort(404)


@main.app_errorhandler(404)
def page_not_found(e):
    """Error 404 handler."""
    logging.error(e)
    return render_template('404.html'), 404


@main.route('/audio/<filename>')
def audio(filename):
    """Serve audio files.

    For local development only. On production, these files are served via
    nginx.
    """
    return send_from_directory(app.config['DIR'] / 'audio', filename)
