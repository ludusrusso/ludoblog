from . import main
from flask import render_template, abort, redirect, url_for

from flask_security import current_user, roles_accepted
from ..models import Post
from .forms import EditBlogPostForm
from .. import db

@main.route('/')
def index():
    return render_template('main/index.html')

@main.route('/posts/id/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('main/post.html', post=post)


@main.route('/posts/new', methods=['post', 'get'])
@roles_accepted('admin', 'publisher')
def get_post():
    form = EditBlogPostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, \
                    body=form.body.data)
        post.author = current_user
        try:
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('main.post', id=post.id))
        except:
            abort(500)
    return render_template('main/edit_post.html', form=form)
