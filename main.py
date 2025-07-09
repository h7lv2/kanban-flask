from src.database import init_db
from src.routes import create_app

def main():
    """Initialize the db and configure app."""
    # Initialize database
    init_db()
    
    # Create and configure the app
    app = create_app()
    app.config['DEBUG'] = True
    app.config['TESTING'] = False
    
    # Run the application
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    main()
