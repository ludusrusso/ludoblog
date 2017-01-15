from . import main
from flask import render_template

from ..models import Post

@main.route('/')
def index():
    return render_template('main/index.html')

@main.route('/posts/id/<int:id>')
def get_post(id):


@main.route('/posts/new')
