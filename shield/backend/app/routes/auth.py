from flask import Blueprint, jsonify, request, session, redirect, url_for
from app.models.user import User
from app.models.organization import Organization
from app.extensions import db
import requests
import os

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')

@bp.route('/github/login')
def github_login():
    return redirect(f'https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&scope=repo user')

@bp.route('/github/callback')
def github_callback():
    code = request.args.get('code')
    
    # Exchange code for access token
    response = requests.post(
        'https://github.com/login/oauth/access_token',
        headers={'Accept': 'application/json'},
        data={
            'client_id': GITHUB_CLIENT_ID,
            'client_secret': GITHUB_CLIENT_SECRET,
            'code': code
        }
    )
    
    access_token = response.json().get('access_token')
    
    # Get user info from GitHub
    user_response = requests.get(
        'https://api.github.com/user',
        headers={'Authorization': f'token {access_token}'}
    )
    github_user = user_response.json()
    
    # Find or create user
    user = User.query.filter_by(email=github_user['email']).first()
    if not user:
        user = User(
            username=github_user['login'],
            email=github_user['email'],
            github_token=access_token
        )
        db.session.add(user)
        db.session.commit()
    
    session['user_id'] = user.id
    return redirect('/dashboard')

@bp.route('/user')
def get_current_user():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    return jsonify(user.to_dict()) 