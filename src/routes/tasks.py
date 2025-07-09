import time
from flask import Blueprint, request, jsonify, g
from sqlalchemy.exc import IntegrityError
import snowflake

from src.database import SessionLocal
from src.models import User, Task, UserTaskAssignment
from src.types.task import VALID_PRIORITIES, VALID_COLUMNS, PRIORITY_MEDIUM, COLUMN_TODO

tasks_bp = Blueprint('tasks', __name__)

# Snowflake ID generator
snowflake_gen = snowflake.SnowflakeGenerator(42)

def get_db_session():
    """Get database session for current request."""
    if 'db' not in g:
        g.db = SessionLocal()
    return g.db

# Task routes
@tasks_bp.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks."""
    db = get_db_session()
    column = request.args.get('column')  # Filter by column if provided
    
    query = db.query(Task)
    if column:
        query = query.filter(Task.current_column == column)
    
    tasks = query.all()
    return jsonify([task.to_dict() for task in tasks])

@tasks_bp.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task by ID."""
    db = get_db_session()
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify(task.to_dict())

@tasks_bp.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if 'title' not in data:
        return jsonify({'error': 'Missing required field: title'}), 400
    
    db = get_db_session()
    
    try:
        # Generate snowflake ID
        task_id = next(snowflake_gen)
        
        # Validate priority if provided
        priority = data.get('priority', PRIORITY_MEDIUM)
        if priority not in VALID_PRIORITIES:
            return jsonify({'error': f'Invalid priority. Must be one of: {VALID_PRIORITIES}'}), 400
        
        # Create task
        task = Task(
            id=task_id,
            title=data['title'],  # Changed from 'name' to 'title'
            description=data.get('description', ''),  # Default to empty string
            priority=priority,  # Added priority field
            date_created=int(time.time()),
            deadline=data.get('deadline'),  # Changed from 'date_deadline' to 'deadline'
            date_completed=data.get('date_completed'),
            current_column=data.get('current_column', COLUMN_TODO)  # Changed default from 'pool' to 'todo'
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

@tasks_bp.route('/api/tasks/<int:task_id>', methods=['PUT'])
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
        if 'title' in data:  # Changed from 'name' to 'title'
            task.title = data['title']
        
        if 'description' in data:
            task.description = data['description']
        
        if 'priority' in data:  # Added priority field handling
            if data['priority'] not in VALID_PRIORITIES:
                return jsonify({'error': f'Invalid priority. Must be one of: {VALID_PRIORITIES}'}), 400
            task.priority = data['priority']
        
        if 'deadline' in data:  # Changed from 'date_deadline' to 'deadline'
            task.deadline = data['deadline']
        
        if 'date_completed' in data:
            task.date_completed = data['date_completed']
        
        if 'current_column' in data:
            if data['current_column'] not in VALID_COLUMNS:
                return jsonify({'error': f'Invalid column. Must be one of: {VALID_COLUMNS}'}), 400
            task.current_column = data['current_column']
            
            # If moving to done, set completion time
            if data['current_column'] == 'done' and not task.date_completed:
                task.date_completed = int(time.time())
        
        db.commit()
        return jsonify(task.to_dict())
    
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/api/tasks/<int:task_id>', methods=['DELETE'])
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
@tasks_bp.route('/api/tasks/<int:task_id>/assign', methods=['POST'])
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

@tasks_bp.route('/api/tasks/<int:task_id>/unassign', methods=['POST'])
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

@tasks_bp.route('/api/assignments', methods=['GET'])
def get_assignments():
    """Get all task assignments."""
    db = get_db_session()
    assignments = db.query(UserTaskAssignment).all()
    return jsonify([assignment.to_dict() for assignment in assignments])
