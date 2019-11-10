from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   session, url_for)

from buzuki import DoesNotExist
from buzuki.admin.forms import PasswordForm, SongForm
from buzuki.decorators import delete_cookie, login_required
from buzuki.sessions import Session
from buzuki.songs import Song

admin = Blueprint('admin', __name__)


@admin.route('/')
@login_required
@delete_cookie('playlist')
def index():
    """A list of all songs in the database."""
    songs = Song.all()
    return render_template(
        'index.html',
        title='Admin',
        songs=songs,
        admin=True,
    )


@admin.route('/add/', methods=['GET', 'POST'])
@login_required
def add():
    """Add a new song to the database."""
    form = SongForm(request.form)

    if request.method == 'POST':
        if form.validate():
            song = Song(
                name=form.name.data,
                artist=form.artist.data,
                scale=form.scale.data,
                rhythm=form.rhythm.data,
                body=form.body.data,
                link=form.link.data,
            )
            song.tofile()
            return redirect(url_for('main.song', slug=song.slug))

    return render_template(
        'admin/songform.html',
        form=form,
        action=url_for('admin.add'),
        title="Νέο τραγούδι",
    )


@admin.route('/save/<slug>/<int:semitones>')
@admin.route('/save/<slug>/<root>')
@login_required
def save(slug, semitones=None, root=None):
    """Save a transposed song to the database."""
    song = Song.get(slug, semitones=semitones, root=root)
    song.tofile()
    return redirect(url_for('main.song', slug=song.slug))


@admin.route('/edit/<slug>', methods=['GET', 'POST'])
@login_required
def edit(slug):
    form = SongForm(request.form)
    song = Song.get(slug)

    if request.method == 'POST' and form.validate():
        song.name = form.name.data
        song.artist = form.artist.data
        song.body = form.body.data
        song.scale = form.scale.data
        song.rhythm = form.rhythm.data
        song.link = form.link.data
        song.tofile()
        return redirect(url_for('main.song', slug=song.slug))

    # Populate form with song's attributes
    form.name.data = song.name
    form.artist.data = song.artist
    form.body.data = song.body
    form.scale.data = song.scale
    form.rhythm.data = song.rhythm
    form.link.data = song.link

    return render_template(
        'admin/songform.html',
        form=form,
        action=url_for('admin.edit', slug=slug),
        title=song.name,
    )


@admin.route('/delete/<slug>')
@login_required
def delete(slug):
    try:
        song = Song.get(slug)
    except DoesNotExist:
        abort(404)
    song.delete()
    return redirect(url_for('main.index'))


@admin.route('/login/', methods=['GET', 'POST'])
def login():
    """Enter admin password to login."""
    form = PasswordForm(request.form)

    if session.get('logged_in'):
        flash("Έχεις ήδη συνδεθεί.", 'info')
        return redirect(url_for('main.index'))

    if request.method == 'GET':
        next_url = request.args.get('next')
        if next_url:
            form.next.data = next_url
    elif request.method == 'POST' and form.validate():
        session['logged_in'] = True
        session['session_id'] = Session.get().session_id
        # If redirected from a page that requires login, redirect back.
        next_url = form.next.data
        if next_url:
            return redirect(next_url)
        return redirect(url_for('main.index'))

    return render_template('admin/login.html', form=form)


@admin.route('/logout/')
@delete_cookie('playlist')
def logout():
    if session.get('logged_in'):
        session['logged_in'] = False
        session['session_id'] = None
    return redirect(request.args.get('next') or url_for('main.index'))
