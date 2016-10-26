from flask import Flask
from flask_wtf import CSRFProtect

from config import config

csrf = CSRFProtect()


def create_app(config_name='default'):
    app = Flask(__name__)

    app.config.from_object(config[config_name])
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    csrf.init_app(app)

    from buzuki.views import main
    app.register_blueprint(main)

    from buzuki.admin.views import admin
    app.register_blueprint(admin, url_prefix='/admin')

    return app
