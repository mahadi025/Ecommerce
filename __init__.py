from flask import Flask
from flask_mongoengine import MongoEngine
from flask_admin import Admin
from flask_uploads import UploadSet, configure_uploads, IMAGES

from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask import redirect, url_for, session, flash
from functools import wraps


photos = UploadSet('images', IMAGES)


app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['DEBUG'] = True
app.config['MONGODB_SETTINGS'] = {
    'db': 'ecommerce',
    'host': 'localhost',
    'port': 27017
}


app.config['UPLOADED_IMAGES_DEST'] = 'static/images/'
app.config['UPLOAD_FOLDER'] = 'static'
configure_uploads(app, (photos))
db = MongoEngine(app)
admin = Admin(app, name='My Admin')
login_manager = LoginManager()

csrf = CSRFProtect(app)


def csrf_exempt(view):
    @wraps(view)
    def decorated(*args, **kwargs):
        return view(*args, **kwargs)
    return decorated


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login'))
    return wrap


def start():
    return app, admin
