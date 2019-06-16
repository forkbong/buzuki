import os
from pathlib import Path

TESTDIR = '/tmp/buzuki_test/'


class Config:
    PWHASH = os.environ.get('BUZUKI_PWHASH')
    SECRET_KEY = os.environ.get('BUZUKI_SECRET_KEY')
    DIR = Path(os.environ.get('BUZUKI_DIR', TESTDIR))


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    PWHASH = 'pbkdf2:md5:1000$p8KuXd4u$0d0f29842d6c5a3e3401bd4dcea0785d'
    SECRET_KEY = 'sekrit'
    DIR = Path(TESTDIR)
    SERVER_NAME = 'localhost.localdomain'
    TESTING = True
    WTF_CSRF_ENABLED = False


config = {
    'default': Config,
    'development': DevelopmentConfig,
    'testing': TestingConfig,
}
