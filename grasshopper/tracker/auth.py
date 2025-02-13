import functools
from datetime import timedelta

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask_jwt_extended import create_access_token


from grasshopper.tracker.model.user import User, UserAlreadyExistsError

bp = Blueprint('auth', __name__, url_prefix='/auth')


def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.find_by_id(user_id)


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not email:
            error = 'Email is required.'

        if error is None:
            try:
                User.create(username, email, password)
            except UserAlreadyExistsError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        user = User.find_by_username(username)
        if user is None:
            error = 'Incorrect username.'
        elif not user.check_password(password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            g.user = user

            return redirect(url_for('dashboard.index'))

        flash(error)

    return render_template('auth/login.html')


@login_required
@bp.route('/logout')
def logout():
    session.clear()
    g.user = None
    return redirect(url_for('index'))


@login_required
@bp.route('/jwt')
def jwt():
    user_id = session.get('user_id')
    if user_id is None:
        flash('You need to be logged in to access this page...', 'error')
        return redirect(url_for('auth.login'))

    user = User.find_by_id(user_id)
    if user is None:
        return redirect(url_for('auth.login'))

    jwt_token = create_access_token(identity=user.username,
                                    expires_delta=timedelta(hours=2))
    g.jwt_token = jwt_token
    return render_template('auth/jwt.html')
