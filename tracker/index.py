from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from flask import current_app, g

bp = Blueprint('index', __name__)

@bp.route('/')
def index():
    return render_template('index.html')