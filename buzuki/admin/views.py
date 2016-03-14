from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, session, url_for)
from sqlalchemy.exc import OperationalError
from werkzeug.security import check_password_hash

from buzuki import db
from buzuki.admin.forms import PasswordForm, SongForm
from buzuki.decorators import login_required
from buzuki.models import Song
from buzuki.utils import Transposer, export_song

admin = Blueprint('admin', __name__)


@admin.route('/')
@login_required
def index():
    """Simple CRUD interface."""
    try:
        songs = Song.query.order_by(Song.name).all()
    except OperationalError:
        songs = []
    return render_template('admin/admin.html', songs=songs)


@admin.route('/add/', methods=['GET', 'POST'])
@login_required
def add():
    """Add a new song to the database."""
    form = SongForm(request.form)

    if request.method == 'POST' and form.validate():
        song = Song(
            name=form.name.data,
            artist=form.artist.data,
            body=form.body.data,
            link=form.link.data,
        )
        db.session.add(song)
        db.session.commit()
        export_song(song)
        flash("{} was successfully added.".format(song.name), 'success')
        return redirect(url_for('main.song', slug=song.slug))

    return render_template(
        'admin/songform.html',
        form=form,
        action=url_for('admin.add'),
        legend="Νέο τραγούδι",
    )


@admin.route('/save/<int:id>/<int:semitones>')
@login_required
def save(id, semitones):
    """Save a transposed song to the database."""
    song = Song.query.get_or_404(id)
    song.body = Transposer(song.body).transpose(semitones)
    db.session.commit()
    export_song(song)
    flash("{} was successfully updated.".format(song.name), 'success')
    return redirect(url_for('main.song', slug=song.slug))


@admin.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    form = SongForm(request.form)
    song = Song.query.get_or_404(id)

    if request.method == 'POST' and form.validate():
        song.name = form.name.data
        song.artist = form.artist.data
        song.body = form.body.data
        song.link = form.link.data
        db.session.commit()
        export_song(song)
        flash("{} was successfully updated.".format(song.name), 'success')
        return redirect(url_for('main.song', slug=song.slug))

    # Populate form with song's attributes
    form.name.data = song.name
    form.artist.data = song.artist
    form.body.data = song.body
    form.link.data = song.link

    return render_template(
        'admin/songform.html',
        form=form,
        action=url_for('admin.edit', id=id),
        legend=song.name,
    )


@admin.route('/delete/<int:id>')
@login_required
def delete(id):
    song = Song.query.get(id)
    if song is not None:
        db.session.delete(song)
        db.session.commit()
        flash("{} was successfully deleted.".format(song.name), 'success')
    else:
        flash("There is no song with id {}.".format(id), 'warning')
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
            flash("You are now logged in.", 'success')
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
        flash("Logged out successfully.", 'success')
    return redirect(url_for('main.index'))
