import json
import urllib.parse
from functools import wraps

from flask import flash, make_response, redirect, request, session, url_for

from buzuki.playlists import get_selected_playlist
from buzuki.songs import Song


def login_required(f):
    """Redirect to the login page if not already logged in."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            flash("Συνδέσου για να συνεχίσεις.", 'info')
            url = url_for('admin.login', next=request.path)
            return redirect(urllib.parse.unquote(url))
        return f(*args, **kwargs)

    return wrapper


def add_slug_to_cookie(f):
    """Add the slug of the viewed song, to the 'latest_songs' cookie."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        playlist = get_selected_playlist()
        num_songs = playlist.num if playlist else len(Song.all())
        limit = int(0.9 * num_songs)

        response = make_response(f(*args, **kwargs))

        cookie = request.cookies.get('latest_songs')
        latest_songs = json.loads(cookie) if cookie else []
        slug = kwargs['slug']
        latest_songs.sort(key=slug.__eq__)  # Move to end
        if not latest_songs or latest_songs[-1] != slug:
            latest_songs.append(slug)
        len_cookie = len(latest_songs)
        if len_cookie > limit:
            latest_songs = latest_songs[len_cookie - limit:]
        response.set_cookie('latest_songs', json.dumps(latest_songs))
        return response

    return wrapper


def set_cookie(key, accessor):
    """Set cookie `key` to the value of the `accessor` argument."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            response = make_response(f(*args, **kwargs))
            response.set_cookie(key, kwargs[accessor])
            return response

        return wrapper

    return decorator


def delete_cookie(key):
    """Delete cookie `key`."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            response = make_response(f(*args, **kwargs))
            response.delete_cookie(key)
            return response

        return wrapper

    return decorator
