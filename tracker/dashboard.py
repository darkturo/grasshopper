from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from tracker.auth import login_required
from tracker.model.db import get_db

bp = Blueprint('dashboard', __name__)

@login_required
@bp.route('/')
def index():
    #db = get_db()
    return render_template('dashboard/index.html', test_runs=[])
