from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, session, url_for)
from werkzeug.security import check_password_hash

from buzuki.admin.forms import PasswordForm, SongForm
from buzuki.decorators import login_required
from buzuki.songs import Song

admin = Blueprint('admin', __name__)


@admin.route('/')
@login_required
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
        if not form.validate():
            flash("All fields are required.", 'danger')
        else:
            song = Song(
                name=form.name.data,
                artist=form.artist.data,
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
        song.link = form.link.data
        song.tofile()
        return redirect(url_for('main.song', slug=song.slug))

    # Populate form with song's attributes
    form.name.data = song.name
    form.artist.data = song.artist
    form.body.data = song.body
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
    song = Song.get(slug)
    song.delete()
    return redirect(url_for('main.index'))


@admin.route('/login/', methods=['GET', 'POST'])
def login():
    """Enter admin password to login."""
    form = PasswordForm(request.form)

    if session.get('logged_in'):
        flash("Έχεις ήδη συνδεθεί.", 'info')
        return redirect(url_for('main.index'))

    if request.method == 'POST' and form.validate():
        password = form.password.data.encode()
        pwhash = current_app.config['PWHASH']
        if check_password_hash(pwhash, password):
            session['logged_in'] = True
            # If redirected from a page that requires login, redirect back.
            if 'next_url' in session:
                next_url = session['next_url']
                del session['next_url']
                return redirect(next_url)
            return redirect(url_for('main.index'))
        else:
            flash("Incorrect password.", 'danger')

    return render_template('admin/login.html', form=form)


@admin.route('/logout/')
def logout():
    if session.get('logged_in'):
        session['logged_in'] = False
    return redirect(url_for('main.index'))
