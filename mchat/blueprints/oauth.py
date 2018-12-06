import os

from flask import flash,redirect,url_for,Blueprint,abort
from flask_login import login_user,current_user

from mchat.extensions import oauth,db
from mchat.models import User

oauth_bp=Blueprint('oauth',__name__)

github=oauth.remote_app(
    name='github',
    consumer_key=os.getenv('GITHUB_CLIENT_ID'),
    consumer_secret=os.getenv('GITHUB_CLIENT_SECRET'),
    request_token_params={'scope':'user'},
    base_url='https://api.github.com',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
)

providers={
    'github':github,
}

profile_endpoints={
    'github':'user',
}

def get_social_profile(provider,access_token):
    profile_endpoint=profile_endpoints[provider.name]
    response=provider.get(profile_endpoint,token=access_token)

    if provider.name=='github':
        username=response.data.get('name')
        website=response.data.get('blog')
        github=response.data.get('html_url')
        email=response.data.get('email')
        bio=response.data.get('bio')
    return username,website,github,email,bio


@oauth_bp.route('/login/<provider_name>')
def oauth_login(provider_name):
    if provider_name not in providers.keys():
        abort(404)
    if current_user.is_authenticated:
        return redirect(url_for('chat.home'))


    callback=url_for('.oauth_callback',provider_name=provider_name,_external=True)
    return providers[provider_name].authorize(callback=callback)

@oauth_bp.route('/callback/<provider_name>')
def oauth_callback(provider_name):
    if provider_name not in providers.keys():
        abort(404)

    provider=providers[provider_name]
    response=provider.authorized_response()

    if response is not None:
        access_token=response.get('access_token')
    else:
        access_token=None

    if access_token is None:
        flash('Access denied,please try again.')
        return redirect(url_for('auth.login'))

    username,website,github,email,bio=get_social_profile(provider,access_token)

    user=User.query.filter_by(email=email).first()
    if user is None:
        user=User(email=email,nickname=username,website=website,github=github,bio=bio)
        db.session.add(user)
        db.session.commit()
        login_user(user,remember=True)
        return redirect(url_for('chat.profile'))
    login_user(user,remember=True)
    return redirect(url_for('chat.home'))