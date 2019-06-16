from pathlib import Path

import pytest

from buzuki import cache_utils, create_app
from buzuki.songs import Song


@pytest.fixture(scope='function')
def client():
    app = create_app('testing')
    directory: Path = app.config['DIR'] / 'songs'
    directory.mkdir(mode=0o755, parents=True, exist_ok=True)
    context = app.app_context()
    context.push()

    yield app.test_client()

    Song.delete_all()
    cache_utils.clear()
    context.pop()
