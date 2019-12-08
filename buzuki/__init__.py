import hashlib
import logging
import os.path
from datetime import datetime

from cachelib import RedisCache
from flask import Flask
from flask_wtf import CSRFProtect
from werkzeug.security import safe_join

from config import config

csrf = CSRFProtect()
cache = RedisCache(default_timeout=0, key_prefix='buzuki_cache_')


class DoesNotExist(Exception):
    pass


class InvalidNote(Exception):
    pass


# Based on https://gist.github.com/mfenniak/2978805
# but we don't check the file modtime for performance.
class FileHashFlask(Flask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._hash_cache = {}

    def inject_url_defaults(self, endpoint, values):
        super().inject_url_defaults(endpoint, values)
        if endpoint == 'static' and 'filename' in values:
            filepath = safe_join(self.static_folder, values['filename'])
            h = self._hash_cache.get(filepath)
            if h is not None:
                values['h'] = h
                return
            if os.path.isfile(filepath):
                h = hashlib.md5()
                with open(filepath, 'rb') as f:
                    h.update(f.read())
                h = h.hexdigest()
                self._hash_cache[filepath] = h
                values['h'] = h


def create_app(config_name='default', production=False):
    app = FileHashFlask(__name__)

    app.config.from_object(config[config_name])
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        filename=app.config['LOGFILE'],
        filemode='w',
    )

    @app.context_processor
    def context():
        return {
            'current_year': datetime.utcnow().year,
            'production': production,
        }

    @app.shell_context_processor
    def shell_context():
        from buzuki.artists import Artist
        from buzuki.playlists import Playlist
        from buzuki.scales import Scale
        from buzuki.sessions import Session
        from buzuki.songs import Song
        return {
            'app': app,
            'Artist': Artist,
            'Song': Song,
            'Scale': Scale,
            'Playlist': Playlist,
            'Session': Session,
        }

    csrf.init_app(app)

    from buzuki.views import main
    app.register_blueprint(main)

    from buzuki.api.views import api
    app.register_blueprint(api, url_prefix='/api')

    from buzuki.admin.views import admin
    app.register_blueprint(admin, url_prefix='/admin')

    cache.clear()

    return app
