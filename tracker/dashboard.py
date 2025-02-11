from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from tracker.auth import login_required
from tracker.model.db import get_db

bp = Blueprint('dashboard', __name__)

@login_required
@bp.route('/dashboard')
def index():
    #db = get_db()
    return render_template('dashboard/main.html', test_runs=[])
