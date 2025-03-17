from app import app, db
from models import User

with app.app_context():
    # Create an admin user
    admin = User(username="admin", role="Admin")
    admin.set_password("admin123")

    # Save to database
    db.session.add(admin)
    db.session.commit()
