from datetime import datetime

from flask import Flask
from flask_caching import Cache
from flask_wtf import CSRFProtect

from config import config

csrf = CSRFProtect()
cache = Cache(config={'CACHE_TYPE': 'simple'})


def create_app(config_name='default'):
    app = Flask(__name__)

    app.config.from_object(config[config_name])
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    @app.context_processor
    def current_year():
        return {'current_year': datetime.utcnow().year}

    @app.shell_context_processor
    def shell_context():
        from buzuki.artists import Artist
        from buzuki.scales import Scale
        from buzuki.songs import Song
        return {
            'app': app,
            'Artist': Artist,
            'Song': Song,
            'Scale': Scale,
        }

    csrf.init_app(app)
    cache.init_app(app)

    from buzuki.views import main
    app.register_blueprint(main)

    from buzuki.api.views import api
    app.register_blueprint(api, url_prefix='/api')

    from buzuki.admin.views import admin
    app.register_blueprint(admin, url_prefix='/admin')

    return app
