from flask import Blueprint, request, jsonify, g
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from src.database import SessionLocal
from src.models import User

auth_bp = Blueprint('auth', __name__)

# Password hasher
ph = PasswordHasher()

def get_db_session():
    """Get database session for current request."""
    if 'db' not in g:
        g.db = SessionLocal()
    return g.db

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate a user."""
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing username or password'}), 400
    
    db = get_db_session()
    user = db.query(User).filter(User.username == data['username']).first()
    
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    try:
        ph.verify(user.password, data['password'])
        # this practically just does nothing right now lol
        # ideally id need to pass a jwt token here and then work with that 
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict()
        }), 200
    except VerifyMismatchError:
        return jsonify({'error': 'Invalid credentials'}), 401
