import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    PWHASH = os.environ.get('BUZUKI_PWHASH')
    SECRET_KEY = os.environ.get('BUZUKI_SECRET_KEY')
    SONGDIR = os.environ.get('BUZUKI_SONGDIR')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Future default


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    PWHASH = 'pbkdf2:md5:1000$p8KuXd4u$0d0f29842d6c5a3e3401bd4dcea0785d'
    SECRET_KEY = 'sekrit'
    SONGDIR = '/tmp/buzuki_test'
    SERVER_NAME = 'localhost.localdomain'
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    TESTING = True
    WTF_CSRF_ENABLED = False


config = {
    'default': Config,
    'development': DevelopmentConfig,
    'testing': TestingConfig,
}
