from flask_login import LoginManager
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO
from flask_migrate import Migrate
from flask_oauthlib.client import OAuth

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
moment = Moment()
socketio=SocketIO()
migrate=Migrate()
oauth=OAuth()

@login_manager.user_loader
def load_user(user_id):
    from mchat.models import User
    return User.query.get(int(user_id))

login_manager.login_view='auth.login'