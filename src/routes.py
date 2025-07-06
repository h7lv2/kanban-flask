import time
from flask import Flask, request, jsonify, g
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import snowflake

from src.database import get_db, SessionLocal
from src.models import User, Task, UserTaskAssignment

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production

# Password hasher
ph = PasswordHasher()

# Snowflake ID generator
snowflake_gen = snowflake.SnowflakeGenerator(42)

def get_db_session():
    """Get database session for current request."""
    if 'db' not in g:
        g.db = SessionLocal()
    return g.db

@app.teardown_appcontext
def close_db(error):
    """Close database session after request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# User routes
@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users."""
    db = get_db_session()
    users = db.query(User).all()
    return jsonify([user.to_dict() for user in users])

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user by ID."""
    db = get_db_session()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict())

@app.route('/api/users', methods=['POST'])
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

@app.route('/api/users/<int:user_id>', methods=['PUT'])
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

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
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

# Task routes
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks."""
    db = get_db_session()
    column = request.args.get('column')  # Filter by column if provided
    
    query = db.query(Task)
    if column:
        query = query.filter(Task.current_column == column)
    
    tasks = query.all()
    return jsonify([task.to_dict() for task in tasks])

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task by ID."""
    db = get_db_session()
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify(task.to_dict())

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if 'name' not in data:
        return jsonify({'error': 'Missing required field: name'}), 400
    
    db = get_db_session()
    
    try:
        # Generate snowflake ID
        task_id = next(snowflake_gen)
        
        # Create task
        task = Task(
            id=task_id,
            name=data['name'],
            description=data.get('description'),
            date_created=int(time.time()),
            date_deadline=data.get('date_deadline'),
            date_completed=data.get('date_completed'),
            current_column=data.get('current_column', 'pool')
        )
        
        db.add(task)
        db.commit()
        
        # Handle assignees if provided
        if 'assignees' in data and data['assignees']:
            for user_id in data['assignees']:
                # Check if user exists
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    assignment = UserTaskAssignment(user_id=user_id, task_id=task_id)
                    db.add(assignment)
            db.commit()
        
        return jsonify(task.to_dict()), 201
    
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update an existing task."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    db = get_db_session()
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    try:
        # Update fields if provided
        if 'name' in data:
            task.name = data['name']
        
        if 'description' in data:
            task.description = data['description']
        
        if 'date_deadline' in data:
            task.date_deadline = data['date_deadline']
        
        if 'date_completed' in data:
            task.date_completed = data['date_completed']
        
        if 'current_column' in data:
            valid_columns = ['pool', 'in_progress', 'testing', 'done']
            if data['current_column'] not in valid_columns:
                return jsonify({'error': f'Invalid column. Must be one of: {valid_columns}'}), 400
            task.current_column = data['current_column']
            
            # If moving to done, set completion time
            if data['current_column'] == 'done' and not task.date_completed:
                task.date_completed = int(time.time())
        
        db.commit()
        return jsonify(task.to_dict())
    
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task."""
    db = get_db_session()
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    try:
        db.delete(task)
        db.commit()
        return jsonify({'message': 'Task deleted successfully'}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

# Task assignment routes
@app.route('/api/tasks/<int:task_id>/assign', methods=['POST'])
def assign_task(task_id):
    """Assign a user to a task."""
    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({'error': 'Missing user_id'}), 400
    
    db = get_db_session()
    
    # Check if task exists
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    # Check if user exists
    user = db.query(User).filter(User.id == data['user_id']).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if assignment already exists
    existing_assignment = db.query(UserTaskAssignment).filter(
        UserTaskAssignment.user_id == data['user_id'],
        UserTaskAssignment.task_id == task_id
    ).first()
    
    if existing_assignment:
        return jsonify({'error': 'User already assigned to this task'}), 400
    
    try:
        assignment = UserTaskAssignment(user_id=data['user_id'], task_id=task_id)
        db.add(assignment)
        db.commit()
        return jsonify(assignment.to_dict()), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>/unassign', methods=['POST'])
def unassign_task(task_id):
    """Unassign a user from a task."""
    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({'error': 'Missing user_id'}), 400
    
    db = get_db_session()
    
    assignment = db.query(UserTaskAssignment).filter(
        UserTaskAssignment.user_id == data['user_id'],
        UserTaskAssignment.task_id == task_id
    ).first()
    
    if not assignment:
        return jsonify({'error': 'Assignment not found'}), 404
    
    try:
        db.delete(assignment)
        db.commit()
        return jsonify({'message': 'User unassigned successfully'}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/assignments', methods=['GET'])
def get_assignments():
    """Get all task assignments."""
    db = get_db_session()
    assignments = db.query(UserTaskAssignment).all()
    return jsonify([assignment.to_dict() for assignment in assignments])

# Authentication routes
@app.route('/api/auth/login', methods=['POST'])
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

# Health check
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': int(time.time())})

if __name__ == '__main__':
    app.run(debug=True)
