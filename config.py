import os


class Config:
    PWHASH = os.environ.get('BUZUKI_PWHASH')
    SECRET_KEY = os.environ.get('BUZUKI_SECRET_KEY')
    SONGDIR = os.environ.get('BUZUKI_SONGDIR')


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    PWHASH = 'pbkdf2:md5:1000$p8KuXd4u$0d0f29842d6c5a3e3401bd4dcea0785d'
    SECRET_KEY = 'sekrit'
    SONGDIR = '/tmp/buzuki_test'
    SERVER_NAME = 'localhost.localdomain'
    TESTING = True
    WTF_CSRF_ENABLED = False


config = {
    'default': Config,
    'development': DevelopmentConfig,
    'testing': TestingConfig,
}
