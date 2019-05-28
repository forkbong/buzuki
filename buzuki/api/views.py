import logging
import re

import elasticsearch
import requests
from flask import Blueprint, abort, jsonify, request

from buzuki import DoesNotExist, InvalidNote, cache_utils, elastic
from buzuki.playlists import Playlist
from buzuki.scales import Scale
from buzuki.songs import Song

api = Blueprint('api', __name__)


@api.route('/')
def index():
    """A list of all songs in the database."""
    return jsonify(cache_utils.get_songs())


@api.route('/songs/<slug>/')
@api.route('/songs/<slug>/<int:semitones>')
@api.route('/songs/<slug>/<root>')
def song(slug, semitones=None, root=None):
    """A song optionally transposed by given semitones."""
    try:
        song = Song.get(slug, semitones=semitones, root=root, unicode=True)
    except DoesNotExist:
        abort(404)
    except InvalidNote as e:
        return jsonify({'message': str(e)}), 400
    return jsonify({
        'name': song.name,
        'artist': song.artist,
        'link': song.link,
        'info': song.info(html=True),
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
    except DoesNotExist:
        abort(404)
    scale.root = root
    return jsonify({
        'name': scale.name,
        'title': scale.title,
        'info': scale.info,
    })


@api.route('/playlists/', methods=['POST'])
def playlists():
    """Add a new playlist."""
    raise NotImplementedError


@api.route('/playlists/<slug>/songs/', methods=['GET', 'POST'])
def playlist_songs(slug):
    """Get list of songs or add a song in a playlist."""
    playlist = Playlist.get(slug)
    if request.method == 'POST':
        data = request.json
        if data is None:
            return jsonify({'message': "No song data given"}), 400

        song_slug = data['slug']
        root = data.get('root')
        try:
            playlist.add(song_slug, root)
        except InvalidNote:
            return jsonify({'message': f"'{root}' is not a valid note"}), 400

    return jsonify(playlist.get_data()['songs'])


@api.route('/playlists/<slug>/songs/<song_slug>', methods=['DELETE'])
def playlist_song(slug, song_slug):
    """Remove a song from a playlist."""
    playlist = Playlist.get(slug)
    playlist.remove(song_slug)
    return jsonify(playlist.get_data()['songs'])


@api.route('/search/<query>/')
def search(query):
    """A list with at most 15 results that match the query."""
    try:
        results = elastic.search(query)['hits']['hits']
    except elasticsearch.ConnectionError:
        return jsonify({'error': "Couldn't connect to elasticsearch"}), 500

    return jsonify(list(result['_source'] for result in results))


@api.route('/autocomplete/')
def autocomplete():
    """A list with at most 15 results that match the query."""
    query = request.args['q']
    url = f'http://localhost:1337/autocomplete/?q={query}'
    return requests.get(url).content


@api.route('/<path>', strict_slashes=False)
def endpoint_not_found(path):
    """Return {} with 404 on any other path."""
    return jsonify({}), 404


@api.errorhandler(404)
def page_not_found(e):
    """Error 404 handler."""
    logging.error(e)
    return jsonify({}), 404


@api.app_errorhandler(405)
def method_not_allowed(e):
    """Error 405 handler."""
    logging.error(e)
    return jsonify({
        'message': 'The method is not allowed for the requested URL'
    }), 405
