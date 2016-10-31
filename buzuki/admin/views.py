from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, session, url_for)
from sqlalchemy.exc import OperationalError
from werkzeug.security import check_password_hash

from buzuki import db
from buzuki.admin.forms import PasswordForm, SongForm
from buzuki.decorators import login_required
from buzuki.models import Song
from buzuki.utils import transpose

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
        song.tofile()
        return redirect(url_for('main.song', slug=song.slug))

    return render_template(
        'admin/songform.html',
        form=form,
        action=url_for('admin.add'),
        legend="Νέο τραγούδι",
    )


@admin.route('/save/<slug>/<int:semitones>')
@login_required
def save(slug, semitones):
    """Save a transposed song to the database."""
    song = Song.query.filter_by(slug=slug).first_or_404()
    song.body = transpose(song.body, semitones)
    db.session.commit()
    song.tofile()
    return redirect(url_for('main.song', slug=song.slug))


@admin.route('/edit/<slug>', methods=['GET', 'POST'])
@login_required
def edit(slug):
    form = SongForm(request.form)
    song = Song.query.filter_by(slug=slug).first_or_404()

    if request.method == 'POST' and form.validate():
        song.name = form.name.data
        song.artist = form.artist.data
        song.body = form.body.data
        song.link = form.link.data
        db.session.commit()
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
        legend=song.name,
    )


@admin.route('/delete/<slug>')
@login_required
def delete(slug):
    song = Song.query.filter_by(slug=slug).first_or_404()
    if song is not None:
        db.session.delete(song)
        db.session.commit()
    else:
        flash("There is no song with slug {}.".format(slug), 'warning')
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
