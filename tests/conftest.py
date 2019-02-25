import os

import pytest

from buzuki import create_app
from buzuki.songs import Song


@pytest.fixture(scope='function')
def client():
    app = create_app('testing')
    os.makedirs(app.config['SONGDIR'], mode=0o755, exist_ok=True)
    context = app.app_context()
    context.push()

    yield app.test_client()

    Song.delete_all()
    context.pop()
