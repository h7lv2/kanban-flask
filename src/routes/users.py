import time
from flask import Blueprint, request, jsonify, g
from sqlalchemy.exc import IntegrityError
from argon2 import PasswordHasher
import snowflake

from src.database import SessionLocal
from src.models import User

users_bp = Blueprint('users', __name__)

# Password hasher
ph = PasswordHasher()

# Snowflake ID generator
snowflake_gen = snowflake.SnowflakeGenerator(42)

def get_db_session():
    """Get database session for current request."""
    if 'db' not in g:
        g.db = SessionLocal()
    return g.db

# User routes
@users_bp.route('/api/users', methods=['GET'])
def get_users():
    """Get all users."""
    db = get_db_session()
    users = db.query(User).all()
    return jsonify([user.to_dict() for user in users])

@users_bp.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user by ID."""
    db = get_db_session()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict())

@users_bp.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['username', 'password', 'display_name']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    db = get_db_session()
    
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == data['username']).first()
    if existing_user:
        return jsonify({'error': 'Username already exists'}), 400
    
    try:
        # Hash password
        hashed_password = ph.hash(data['password'])
        
        # Generate snowflake ID
        user_id = next(snowflake_gen)
        
        # Create user
        user = User(
            id=user_id,
            username=data['username'],
            password=hashed_password,
            display_name=data['display_name'],
            # the png is a lie
            profile_picture=data.get('profile_picture', f'/assets/avatars/{user_id}.png'),
            is_admin=data.get('is_admin', False),
            date_created=int(time.time())
        )
        
        db.add(user)
        db.commit()
        
        return jsonify(user.to_dict()), 201
    
    except IntegrityError:
        db.rollback()
        return jsonify({'error': 'Username already exists'}), 400
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

@users_bp.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update an existing user."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    db = get_db_session()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        # Update fields if provided
        if 'username' in data:
            # Check if new username already exists
            existing_user = db.query(User).filter(User.username == data['username'], User.id != user_id).first()
            if existing_user:
                return jsonify({'error': 'Username already exists'}), 400
            user.username = data['username']
        
        if 'password' in data:
            user.password = ph.hash(data['password'])
        
        if 'display_name' in data:
            user.display_name = data['display_name']
        
        if 'profile_picture' in data:
            user.profile_picture = data['profile_picture']
        
        if 'is_admin' in data:
            user.is_admin = data['is_admin']
        
        db.commit()
        return jsonify(user.to_dict())
    
    except IntegrityError:
        db.rollback()
        return jsonify({'error': 'Username already exists'}), 400
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

@users_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user."""
    db = get_db_session()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        db.delete(user)
        db.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500