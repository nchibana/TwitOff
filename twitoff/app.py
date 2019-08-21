"""Main application, configuration and routing logic for Twitoff"""

from decouple import config
from flask import Flask, render_template, request
from .models import DB, Tweet, User
from .twitter import add_or_update_user

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['ENV'] = config('ENV')
    DB.init_app(app)

    @app.route('/')
    def root():
        users = User.query.all()
        return render_template('base.html', title='Home', users=users)

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return render_template('base.html', title='DB Reset', users=[])

    @app.route('/user', methods=['POST'])
    @app.route('/user/<name>')
    def user(name=None, message=''):
        name = name or request.values['user_name']
        try:
            if request.method == 'POST':
                db_user = add_or_update_user(name)
                message = f"User {db_user.name} successfully added!"
            tweets = User.query.filter(User.name == name).one().tweets
        except Exception as e:
            message = "Error adding or fetching {}: {}".format(name, e)
            tweets = []
        return render_template('user.html', title=name, tweets=tweets, 
                                message=message)

    return app