from flask_restful import Api, reqparse
from flask import Flask, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_user import  UserManager, UserMixin, login_required
from sqlalchemy import exc
import sys


db_name = "imdb_movies.db"

class ConfigClass(object):
    SECRET_KEY = '&4^i$)yvfted^3)%8l3u@&lq$$+h#0r(w72(-kjj5-hn^1mc_u'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + db_name
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    USER_APP_NAME = "Movies API"
    USER_ENABLE_EMAIL = False      # Disable email authentication
    USER_ENABLE_USERNAME = True    # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = False    # Simplify register form


def create_app(first_time=False):

    app = Flask(__name__)
    app.config.from_object(__name__+'.ConfigClass')
    api = Api(app)

    # Initialize Flask-SQLAlchemy
    db = SQLAlchemy(app)


    class User(db.Model, UserMixin):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')
        username = db.Column(db.String(100, collation='NOCASE'), nullable=False, unique=True)
        password = db.Column(db.String(255), nullable=False, server_default='')
        first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
        last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
        roles = db.relationship('Role', secondary='user_roles')

    # Define the Role data-model
    class Role(db.Model):
        __tablename__ = 'roles'
        id = db.Column(db.Integer(), primary_key=True)
        name = db.Column(db.String(50), unique=True)

    # Define the UserRoles association table
    class UserRoles(db.Model):
        __tablename__ = 'user_roles'
        id = db.Column(db.Integer(), primary_key=True)
        user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
        role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))

    db.create_all()

    user_manager = UserManager(app, db, User)

    ## member_page template
    @app.route('/members')
    @login_required
    def member_page():
        return render_template_string("""
            {% extends "flask_user_layout.html" %}
            {% block content %}
                <h2>Members page</h2>
                <p><a href={{ url_for('user.register') }}>Register</a></p>
                <p><a href={{ url_for('user.login') }}>Sign in</a></p>
                <p><a href={{ url_for('home_page') }}>Home page</a> (accessible to anyone)</p>
                <p><a href={{ url_for('member_page') }}>Member page</a> (login required)</p>
                <p><a href={{ url_for('user.logout') }}>Sign out</a></p>
            {% endblock %}
            """)

    ## home_page template
    @app.route('/')
    def home_page():
        return render_template_string("""
            {% extends "flask_user_layout.html" %}
            {% block content %}
                <h2>Home page</h2>
                <p><a href={{ url_for('user.register') }}>Register</a></p>
                <p><a href={{ url_for('user.login') }}>Sign in</a></p>
                <p><a href={{ url_for('home_page') }}>Home page</a> (accessible to anyone)</p>
                <p><a href={{ url_for('member_page') }}>Member page</a> (login required)</p>
                <p><a href={{ url_for('user.logout') }}>Sign out</a></p>
            {% endblock %}
            """)

    if first_time:
        try:
            admin_role = Role(name='Admin')
            user1 = User(
                username='user123',active=True,
                password=user_manager.hash_password('Password1')
            )
            user2 = User(
                username='user234',active=True,
                password=user_manager.hash_password('Password2')
            )
            user1.roles = [admin_role,]
            db.session.add(admin_role)
            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()
        except exc.IntegrityError:
            pass

    ## attaching the url to view
    from views import MovieViewset, AllMoviesViewset

    api.add_resource(MovieViewset, '/movie/<int:movie_id>')
    api.add_resource(AllMoviesViewset, '/allmovies')


    return app


if __name__ == '__main__':

    ## checking for sys args
    sys_args = sys.argv
    run_first_time = False
    if (len(sys_args) > 1) and (sys_args[1]=='first_time'):
        run_first_time = True

    app = create_app(run_first_time)
    app.run(host='0.0.0.0',port=8000, debug=True)
