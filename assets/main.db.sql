-- SQLite database schema for Kanban Flask application
-- Create users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    profile_picture VARCHAR(500),
    is_admin BOOLEAN NOT NULL DEFAULT 0 CHECK(is_admin IN (0, 1)),
    date_created INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create tasks table
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    date_created INTEGER NOT NULL,
    date_deadline INTEGER,
    date_completed INTEGER,
    current_column VARCHAR(20) NOT NULL DEFAULT 'pool' CHECK(current_column IN ('pool', 'in_progress', 'testing', 'done')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create bridge table for user-task assignments (many-to-many relationship)
CREATE TABLE user_task_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    task_id INTEGER NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    UNIQUE(user_id, task_id) -- Prevent duplicate assignments
);

-- Create indexes for better performance
CREATE INDEX idx_tasks_column ON tasks(current_column);
CREATE INDEX idx_tasks_deadline ON tasks(date_deadline);
CREATE INDEX idx_tasks_completed ON tasks(date_completed);
CREATE INDEX idx_assignments_user ON user_task_assignments(user_id);
CREATE INDEX idx_assignments_task ON user_task_assignments(task_id);

-- Insert some sample data for testing
-- Note: Passwords are hashed using Argon2 for security
-- This is just sample data and should be replaced with real user data in production
INSERT INTO users (id, username, password, display_name, profile_picture, is_admin, date_created) VALUES
(1, 'admin', '$argon2id$v=19$m=65536,t=3,p=4$ef9817152253b4453ccafde4515570ad', 'Administrator', '/assets/avatars/1.png', 1, strftime('%s', 'now')),
(2, 'user1', '$argon2id$v=19$m=65536,t=3,p=4$e17555969e4ac6fcef7301a3e60a51e3', 'John Doe', '/assets/avatars/2.png', 0, strftime('%s', 'now')),
(3, 'user2', '$argon2id$v=19$m=65536,t=3,p=4$34f8ca8538519c1bb9c077061f7eea54', 'Jane Smith', '/assets/avatars/3.png', 0, strftime('%s', 'now'));

-- Sample tasks
-- Note: Tasks are created with current date and time
-- Current columns are set to 'pool', 'in_progress', 'testing', or 'done'
-- This is just sample data and should be replaced with real task data in production
INSERT INTO tasks (id, name, description, date_created, current_column) VALUES
(1, 'Setup Database', 'Create SQLite database with proper schema', strftime('%s', 'now'), 'done'),
(2, 'Implement User Authentication', 'Add login and registration functionality', strftime('%s', 'now'), 'in_progress'),
(3, 'Create Task Management UI', 'Build the kanban board interface', strftime('%s', 'now'), 'pool'),
(4, 'Add Task Assignment Feature', 'Allow assigning tasks to users', strftime('%s', 'now'), 'pool');

-- Sample task assignments
-- Note: This is just sample data and should be replaced with real task assignments in production
-- Assign users to tasks
-- This is a many-to-many relationship, so we can assign multiple users to a task
-- and multiple tasks to a user
INSERT INTO user_task_assignments (user_id, task_id) VALUES
(1, 1), -- Admin assigned to Setup Database
(2, 2), -- John assigned to User Authentication
(1, 2), -- Admin also assigned to User Authentication
(3, 3); -- Jane assigned to Task Management UI