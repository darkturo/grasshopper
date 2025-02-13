from flask import (
    Blueprint, render_template
)
from grasshopper.tracker.auth import login_required

bp = Blueprint('dashboard', __name__)


@login_required
@bp.route('/dashboard')
def index():
    # db = get_db()
    return render_template('dashboard/main.html', test_runs=[])
