from datetime import date, datetime

from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from Blog import app, db, login_manager
from Blog.models.comment import Comment
from Blog.models.forms import RegistrationForm, LoginForm, CommentForm, CreatePostForm
from Blog.models.posts import BlogPost
from Blog.models.user import User



@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.context_processor
def inject_user():
    return dict(logged_in=current_user.is_authenticated)

@app.context_processor
def inject_current_year():
    current_year = datetime.now().year
    return dict(current_year=current_year)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first() is not None:
            flash('You have already registered with this email, login instead!')
            return redirect(url_for('login'))
        new_user = User(name=form.name.data,
                         email=form.email.data,
                         password=generate_password_hash(form.password.data))
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('get_all_posts'))
    return render_template("register.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user is None:
            flash("This email doesn't exist, please try again", 'error')
            return render_template('login.html', form=form)
        if check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('get_all_posts'))
        else:
            flash("Password incorrect, please try again", 'error')
            return render_template('login.html', form=form)
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
def show_post(post_id):
    form = CommentForm()
    requested_post = BlogPost.query.get(post_id)
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('You need to login or register to comment')
            return redirect(url_for('login'))
        new_comment = Comment(
            post_id=post_id,
            author_id=current_user.id,
            text=form.comment.data,
            post=requested_post,
            author=current_user
        )
        db.session.add(new_comment)
        db.session.commit()
        form = CommentForm()
    return render_template("post.html", post=requested_post, form=form)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


# def admin_only(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if current_user is None or not current_user.is_authenticated:
#             return abort(403)
#         if current_user.id != 1:
#             return abort(403)
#         return f(*args, **kwargs)
#
#     return decorated_function


@app.route("/new-post", methods=['GET', 'POST'])
@login_required
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            author_id=current_user.id,
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>", methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form)


@app.route("/delete/<int:post_id>")
@login_required
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))
