import re
from itertools import islice

from flask import Blueprint, abort, jsonify

from buzuki.artists import Artist
from buzuki.scales import Scale
from buzuki.songs import Song

api = Blueprint('api', __name__)


@api.route('/')
def index():
    """A list of all songs in the database."""
    songs = Song.all()
    return jsonify([{
        'name': song.name,
        'artist': song.artist,
        'link': song.link,
    } for song in songs])


@api.route('/songs/<slug>/')
@api.route('/songs/<slug>/<int:semitones>')
@api.route('/songs/<slug>/<root>')
def song(slug, semitones=None, root=None):
    """A song optionally transposed by given semitones."""
    song = Song.get(slug, semitones=semitones, root=root, unicode=True)
    return jsonify({
        'name': song.name,
        'artist': song.artist,
        'link': song.link,
        'info': song.body,
    })


@api.route('/scales/<slug>/')
@api.route('/scales/<slug>/<root>')
def scale(slug, root='D'):
    """A list of all available scales."""
    if not re.match('^[A-G][bs]?$', root):
        return jsonify({'message': f"'{root}' is not a valid note"}), 400
    root = re.sub('s', '#', root)
    try:
        scale = Scale.get(slug)
    except (ValueError, KeyError):
        abort(404)
    scale.root = root
    return jsonify({
        'name': scale.name,
        'title': scale.title,
        'info': scale.info,
    })


@api.route('/search/<query>/')
def search(query):
    """A list with at most 15 results that match the query."""

    def do_search(query):
        """Yield songs that match the given query.

        Searches in song names first, and then artist names.
        We skip search in song bodies for performance.
        """
        matched_by_title = []
        for song in Song.search(query):
            matched_by_title.append(song.name)
            yield song.name

        for artist in Artist.search(query):
            yield artist.name

    return jsonify(list(islice(do_search(query), 15)))


@api.route('/<path>', strict_slashes=False)
def endpoint_not_found(path):
    """Return {} with 404 on any other path."""
    return jsonify({}), 404


@api.errorhandler(404)
def page_not_found(e):
    """Error 404 handler."""
    return jsonify({}), 404


@api.app_errorhandler(405)
def method_not_allowed(e):
    """Error 405 handler."""
    return jsonify({
        'message': 'The method is not allowed for the requested URL'
    }), 405
