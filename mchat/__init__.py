import os
import click
from flask import Flask, render_template
from flask_wtf.csrf import CSRFError

from mchat.blueprints.auth import auth_bp
from mchat.blueprints.chat import chat_bp
from mchat.blueprints.oauth import oauth_bp
from mchat.extensions import db,migrate, login_manager, csrf, moment,socketio,oauth
from mchat.models import User, Message
from mchat.settings import config


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('mchat')
    app.config.from_object(config[config_name])

    register_extensions(app)
    register_blueprints(app)
    register_errors(app)
    register_commands(app)

    return app


def register_extensions(app):
    db.init_app(app)
    migrate.init_app(app,db)
    login_manager.init_app(app)
    csrf.init_app(app)
    moment.init_app(app)
    socketio.init_app(app)
    oauth.init_app(app)



def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(oauth_bp)

def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('error.html', description=e.description, code=e.code), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', description=e.description, code=e.code), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error.html', description=e.description, code=e.code), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('error.html', description=e.description, code=e.code), 400


def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop')
    def initdb(drop):
        """Initial database"""
        if drop:
            click.confirm('Will delete the database,continue?', abort=True)
            db.drop_all()
            click.echo('Dropped.')
        db.create_all()
        click.echo('All done.')

    @app.cli.command()
    @click.option('--message', default=300, help='Quantity of messages,default is 300')
    def forge(message):
        """Generate fake data"""
        import random
        from sqlalchemy.exc import IntegrityError

        from faker import Faker

        fake = Faker()

        click.echo('Initial database')
        db.drop_all()
        db.create_all()

        click.echo('Forging data')
        admin = User(nickname='Marc', email='admin@mchat.com')
        admin.set_password('123456')
        db.session.add(admin)
        db.session.commit()

        click.echo('Generating users')
        for i in range(50):
            user = User(
                nickname=fake.name(),
                bio=fake.sentence(),
                github=fake.url(),
                website=fake.url(),
                email=fake.email(),
            )
            db.session.add(user)

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

        click.echo('Generating messages')
        for i in range(message):
            message = Message(
                author=User.query.get(random.randint(1, User.query.count())),
                body=fake.sentence(),
                timestamp=fake.date_time_between('-30d','-2d')
            )
            db.session.add(message)

        db.session.commit()
        click.echo('Done')
