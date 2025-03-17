from app import app, db
from models import User

with app.app_context():
    # Delete any existing admin user
    existing_user = User.query.filter_by(username="admin").first()
    if existing_user:
        db.session.delete(existing_user)
        db.session.commit()
        print("Existing admin user deleted.")

    # Create a new admin user with a properly hashed password
    admin = User(username="admin", role="Admin")
    admin.set_password("admin123")  # Hashes password

    # Save to database
    db.session.add(admin)
    db.session.commit()

    print("New admin user created successfully!")
