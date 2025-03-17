from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from forms import InventoryForm, CheckoutForm, UserForm, UpdateUserForm, AddInventoryForm
from models import db, User, Inventory, Loan, Log, ChangeLog
from datetime import datetime



app = Flask(__name__)
app.config.from_object('config.Config')

db.init_app(app)
migrate = Migrate(app, db)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Redirects unauthorized users to login page
login_manager.login_message = "Please log in to access this page."

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))  # Corrected for SQLAlchemy 2.0

# ---- AUTHENTICATION ROUTES ---- #
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password.", "danger")

    return render_template('login.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for('login'))

# ---- USER MANAGEMENT ---- #
@app.route('/admin/users/manage', methods=['GET', 'POST'])
@login_required
def manage_users():
    if not current_user.is_admin():
        flash("You do not have permission to manage users.", "danger")
        return redirect(url_for('index'))

    form = UserForm()
    users = User.query.all()

    if form.validate_on_submit():
        new_user = User(username=form.username.data, role=form.role.data)
        new_user.set_password(form.password.data)  # ✅ Secure password hashing
        db.session.add(new_user)
        db.session.commit()
        flash(f"User {new_user.username} added successfully!", "success")
        return redirect(url_for('manage_users'))  # ✅ Reloads page to show the new user

    return render_template('manage_users.html', form=form, users=users)

@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin():
        flash("You do not have permission to edit users.", "danger")
        return redirect(url_for('manage_users'))

    user = User.query.get_or_404(user_id)
    form = UpdateUserForm(obj=user)

    if form.validate_on_submit():
        user.username = form.username.data
        user.role = form.role.data
        if form.password.data:
            user.set_password(form.password.data)  # ✅ Only update if a new password is provided
        db.session.commit()
        flash(f"User {user.username} updated successfully!", "success")
        return redirect(url_for('manage_users'))

    return render_template('edit_user.html', form=form, user=user)


@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin():
        flash("You do not have permission to delete users.", "danger")
        return redirect(url_for('manage_users'))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f"User {user.username} has been deleted.", "success")
    return redirect(url_for('manage_users'))

# ---- HOME/INVENTORY LIST ---- #
@app.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)  # Get the page number from the URL (default is 1)
    per_page = 25  # Number of items per page

    # Get filtering parameters
    query = request.args.get('query', '', type=str).strip()
    asset_type = request.args.get('asset_type', '', type=str)
    site_name = request.args.get('site_name', '', type=str)
    assigned_to = request.args.get('assigned_to', '', type=str)
    sort_by = request.args.get('sort_by', 'asset_tag', type=str)

    # Start with a base query
    inventory_query = Inventory.query

    # Apply filters
    if query:
        inventory_query = inventory_query.filter(
            (Inventory.asset_tag.ilike(f"%{query}%")) |
            (Inventory.asset_type.ilike(f"%{query}%")) |
            (Inventory.site_name.ilike(f"%{query}%")) |
            (Inventory.assigned_to.ilike(f"%{query}%"))
        )

    if asset_type:
        inventory_query = inventory_query.filter(Inventory.asset_type.ilike(f"%{asset_type}%"))
    
    if site_name:
        inventory_query = inventory_query.filter(Inventory.site_name.ilike(f"%{site_name}%"))
    
    if assigned_to:
        inventory_query = inventory_query.filter(Inventory.assigned_to.ilike(f"%{assigned_to}%"))

    # Sorting logic
    if sort_by == "asset_tag":
        inventory_query = inventory_query.order_by(Inventory.asset_tag)
    elif sort_by == "site_name":
        inventory_query = inventory_query.order_by(Inventory.site_name)
    elif sort_by == "assigned_to":
        inventory_query = inventory_query.order_by(Inventory.assigned_to)

    # Apply pagination
    inventory = inventory_query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('inventory.html', inventory=inventory, query=query, asset_type=asset_type, site_name=site_name, assigned_to=assigned_to, sort_by=sort_by)

@app.route('/search')
def search():
    query = request.args.get('query', '', type=str).strip()
    category = request.args.get('category', '', type=str)
    sort_by = request.args.get('sort_by', 'asset_tag', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = 25

    # Start with a base query
    search_query = Inventory.query

    # Apply search filter on relevant fields
    if query:
        search_query = search_query.filter(
            (Inventory.asset_tag.ilike(f"%{query}%")) |
            (Inventory.asset_type.ilike(f"%{query}%")) |
            (Inventory.site_name.ilike(f"%{query}%")) |
            (Inventory.assigned_to.ilike(f"%{query}%"))
        )

    # Filter by category (if provided)
    if category:
        search_query = search_query.filter(Inventory.asset_type == category)

    # Sorting logic
    if sort_by == "asset_tag":
        search_query = search_query.order_by(Inventory.asset_tag)
    elif sort_by == "site_name":
        search_query = search_query.order_by(Inventory.site_name)
    elif sort_by == "assigned_to":
        search_query = search_query.order_by(Inventory.assigned_to)

    # Apply pagination
    inventory_items = search_query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('inventory.html', inventory=inventory_items, query=query, category=category, sort_by=sort_by)

# ---- INVENTORY MANAGEMENT ---- #

@app.route('/inventory/add', methods=['GET', 'POST'])
@login_required
def add_inventory():
    if current_user.is_reader():  # ❌ Readers cannot add inventory
        flash("You do not have permission to add inventory.", "danger")
        return redirect(url_for('index'))

    form = InventoryForm()
    if form.validate_on_submit():
        new_item = Inventory(
            site_name=form.site_name.data,
            room_number=form.room_number.data,
            room_name=form.room_name.data,
            asset_tag=form.asset_tag.data,
            asset_type=form.asset_type.data,
            model=form.model.data,
            serial_number=form.serial_number.data,
            notes=form.notes.data,
            assigned_to=form.assigned_to.data,
            date_assigned=form.date_assigned.data,
            date_decommissioned=form.date_decommissioned.data
        )
        db.session.add(new_item)
        db.session.commit()
        flash(f"Inventory item {new_item.asset_tag} added successfully!", "success")
        return redirect(url_for('inventory'))

    return render_template('add_inventory.html', form=form)


@app.route('/inventory/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_inventory(item_id):
    if not (current_user.is_admin() or current_user.is_editor()):
        flash("You do not have permission to edit inventory.", "danger")
        return redirect(url_for('index'))

    item = Inventory.query.get_or_404(item_id)
    form = InventoryForm(obj=item)

    if form.validate_on_submit():
        # Log changes
        change_desc = f"Edited: {item.name} (Category: {item.category}, Status: {item.status})"
        log_entry = ChangeLog(item_id=item.id, user_id=current_user.id, change_description=change_desc)
        db.session.add(log_entry)

        # Update item details
        item.name = form.name.data
        item.category = form.category.data
        item.status = form.status.data
        item.assigned_to = form.assigned_to.data
        item.is_loaner = form.is_loaner.data
        
        db.session.commit()
        flash("Inventory item updated!", "success")
        return redirect(url_for('index'))

    return render_template('edit_inventory.html', form=form, item=item)

@app.route('/inventory/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_inventory(item_id):
    if not current_user.is_admin():  # ❌ Only Admins can delete inventory
        flash("You do not have permission to delete inventory.", "danger")
        return redirect(url_for('index'))

    item = Inventory.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash("Inventory item deleted!", "success")
    return redirect(url_for('index'))

@app.route('/inventory/checkout/<int:item_id>', methods=['GET', 'POST'])
@login_required
def checkout_inventory(item_id):
    if not current_user.is_admin():
        flash("Only Admins can check out items.", "danger")
        return redirect(url_for('index'))

    item = Inventory.query.get_or_404(item_id)

    if not item.is_loaner:
        flash("This item is not available as a loaner.", "danger")
        return redirect(url_for('index'))

    form = CheckoutForm()
    if form.validate_on_submit():
        user = User.query.filter(User.username.ilike(form.user_name.data)).first()

        if not user:
            flash("User not found.", "danger")
            return redirect(url_for('checkout_inventory', item_id=item.id))

        loan = Loan(item_id=item.id, user_name=user.username, checkout_date=datetime.utcnow())
        item.status = "Checked Out"
        item.assigned_to = user.username
        db.session.add(loan)
        db.session.commit()
        flash(f"{item.name} has been checked out to {user.username}.", "success")
        return redirect(url_for('index'))

    return render_template('checkout.html', form=form, item=item)

@app.route('/inventory/return/<int:loan_id>', methods=['POST'])
@login_required
def return_inventory(loan_id):
    loan = Loan.query.get_or_404(loan_id)

    if loan.return_date:
        flash("This item has already been returned.", "warning")
        return redirect(url_for('index'))

    loan.return_date = datetime.utcnow()
    loan.inventory_item.status = "Available"
    loan.inventory_item.assigned_to = None

    # ✅ **Log the return action**
    log = Log(action="Returned", user=current_user.username, item_name=loan.inventory_item.name, timestamp=datetime.utcnow())
    db.session.add(log)

    db.session.commit()
    flash(f"{loan.inventory_item.name} has been returned.", "success")
    return redirect(url_for('index'))

@app.route('/logs')
@login_required
def logs():
    if current_user.role != "Admin":
        flash("Admins only!", "danger")
        return redirect(url_for('index'))

    logs = Log.query.order_by(Log.timestamp.desc()).all()
    return render_template('logs.html', logs=logs)

@app.route('/inventory/details/<int:item_id>')
@login_required
def item_details(item_id):
    item = Inventory.query.get_or_404(item_id)
    loan_history = Loan.query.filter_by(item_id=item.id).order_by(Loan.checkout_date.desc()).all()
    
    return render_template('item_details.html', item=item, loan_history=loan_history)
