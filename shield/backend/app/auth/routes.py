from flask import Blueprint, request, jsonify
from app.models import User
from app.extensions import db
import jwt
from datetime import datetime, timedelta
from functools import wraps
import os

auth_bp = Blueprint('auth', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, os.environ.get('JWT_SECRET_KEY', 'super-secret-key'), algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
            
        return f(current_user, *args, **kwargs)
    
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Check if user already exists
    user = User.query.filter_by(email=data.get('email')).first()
    if user:
        return jsonify({'message': 'User already exists'}), 400
    
    new_user = User(
        username=data.get('username'),
        email=data.get('email'),
        role=data.get('role', 'user'),
        organization_id=data.get('organization_id')
    )
    new_user.set_password(data.get('password'))
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email and password are required'}), 400
    
    user = User.query.filter_by(email=data.get('email')).first()
    
    if not user or not user.check_password(data.get('password')):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    # Generate JWT token
    token = jwt.encode(
        {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=24)
        },
        os.environ.get('JWT_SECRET_KEY', 'super-secret-key'),
        algorithm='HS256'
    )
    
    return jsonify({
        'token': token,
        'user': user.to_dict()
    })

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify(current_user.to_dict()) 