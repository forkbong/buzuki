#!/usr/bin/env python3

import sys
from multiprocessing import cpu_count

import click
import IPython
from flask import current_app as app
from flask.cli import FlaskGroup, with_appcontext
from gunicorn.app.base import BaseApplication
from gunicorn.config import Config as GunicornConfig
from IPython.terminal.ipapp import load_default_config

from buzuki import create_app


@click.group(cls=FlaskGroup, create_app=lambda: create_app('default'))
def cli():
    """Management script for buzuki."""


@cli.command(context_settings=dict(ignore_unknown_options=True))
@click.argument('ipython_args', nargs=-1, type=click.UNPROCESSED)
@with_appcontext
def shell(ipython_args):
    """Run a shell in the app context.

    Runs an interactive Python shell in the context of a given Flask
    application. The application will populate the default namespace of this
    shell according to it's configuration.

    This is useful for executing small snippets of management code without
    having to manually configuring the application.
    """
    # See: https://github.com/ei-grad/flask-shell-ipython
    config = load_default_config()
    config.TerminalInteractiveShell.banner1 = (
        f"Python {sys.version} on {sys.platform}\n"
        f"IPython: {IPython.__version__}\n"
        f"App: {app.import_name}{' [debug]' if app.debug else ''}\n"
        f"Instance: {app.instance_path}\n"
    )

    IPython.start_ipython(
        argv=ipython_args,
        user_ns=app.make_shell_context(),
        config=config,
    )


@cli.command()
@click.option('-w', '--workers', help="Number of workers.",
              default=2 * cpu_count() + 1)
@click.option('-h', '--host', help="The interface to bind to.",
              default='127.0.0.1')
@click.option('-p', '--port', help="The port to bind to.", default=8000)
def gunicorn(workers, host, port):
    """Run a production server with gunicorn."""

    class GunicornApplication(BaseApplication):
        def load_config(self):
            assert isinstance(self.cfg, GunicornConfig)
            self.cfg.set('bind', f'{host}:{port}')
            self.cfg.set('workers', workers)

        def load(self):
            return create_app()

    GunicornApplication().run()


if __name__ == '__main__':
    cli()
