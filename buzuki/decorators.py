from functools import wraps

from flask import flash, redirect, request, session, url_for


def login_required(f):
    """Redirect to the login page if not already logged in."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            flash("Συνδέσου για να συνεχίσεις.", 'info')
            # Store url in session to redirect back
            session['next_url'] = request.url
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)

    return wrapper
