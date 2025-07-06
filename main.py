from flask import Flask
from src.database import init_db
from src.routes import app

def create_app():
    """Initialize the db and configure app."""
    # Initialize database
    init_db()
    
    # Configure the app
    app.config['DEBUG'] = True
    app.config['TESTING'] = False
    
    return app

def main():
    app = create_app()
    
    # Run the application
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    main()
