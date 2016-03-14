import pytest

from buzuki import create_app, db


@pytest.fixture(scope='function')
def client():
    app = create_app('testing')
    context = app.app_context()
    context.push()
    db.create_all()

    yield app.test_client()

    db.session.remove()
    db.drop_all()
    context.pop()
