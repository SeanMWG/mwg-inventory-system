from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from forms import InventoryForm, CheckoutForm, UserForm, UpdateUserForm, AddInventoryForm, EditInventoryForm, LoginForm
from models import db, User, Inventory, Loan, Log, ChangeLog, Checkout
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
    form = LoginForm()  # ✅ Ensure the form is instantiated

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password.", "danger")

    return render_template('login.html', form=form)  # ✅ Pass 'form' to template

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
    if not (current_user.is_admin() or current_user.is_editor()):
        flash("You do not have permission to add inventory.", "danger")
        return redirect(url_for('index'))

    form = InventoryForm()

    if form.validate_on_submit():
        existing_item = Inventory.query.filter_by(asset_tag=form.asset_tag.data).first()
        
        if existing_item:
            flash("An item with this asset tag already exists!", "warning")
            return redirect(url_for('add_inventory'))

        # Create new inventory item with all fields
        new_item = Inventory(
            # Basic information
            site_name=form.site_name.data,
            asset_tag=form.asset_tag.data,
            asset_type=form.asset_type.data,
            model=form.model.data,
            serial_number=form.serial_number.data,
            notes=form.notes.data if form.notes.data else None,
            
            # Location information
            room_number=form.room_number.data,
            room_name=form.room_name.data,
            
            # Assignment information
            assigned_to=form.assigned_to.data,
            date_assigned=form.date_assigned.data,
            date_decommissioned=form.date_decommissioned.data,
            
            # Category
            category=request.form.get('category', ''),
            
            # Loaner status
            is_loaner=form.is_loaner.data
        )

        db.session.add(new_item)
        
        # Add a log entry for the new item
        log_entry = Log(
            action="Item Added",
            user=current_user.username,
            item_name=f"{new_item.asset_tag} ({new_item.asset_type})",
            timestamp=datetime.utcnow()
        )
        db.session.add(log_entry)
        
        db.session.commit()
        flash("Inventory item added successfully!", "success")
        return redirect(url_for('item_details', item_id=new_item.id))

    return render_template('add_inventory.html', form=form)


@app.route('/inventory/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_inventory(item_id):
    if not (current_user.is_admin() or current_user.is_editor()):
        flash("You do not have permission to edit inventory.", "danger")
        return redirect(url_for('index'))

    item = Inventory.query.get_or_404(item_id)  # Fetch item
    form = InventoryForm(obj=item)  # Pre-fill form

    if form.validate_on_submit():
        # Update basic information
        item.site_name = form.site_name.data
        item.asset_tag = form.asset_tag.data
        item.asset_type = form.asset_type.data
        item.model = form.model.data
        item.serial_number = form.serial_number.data
        item.notes = form.notes.data
        
        # Update location information
        item.room_number = form.room_number.data
        item.room_name = form.room_name.data
        
        # Update assignment information
        item.assigned_to = form.assigned_to.data
        item.date_assigned = form.date_assigned.data
        item.date_decommissioned = form.date_decommissioned.data
        
        # Update category (from the custom form field)
        item.category = request.form.get('category', '')
        
        # Update loaner status
        item.is_loaner = 'is_loaner' in request.form
        
        # Add a change log entry
        change_log = ChangeLog(
            item_id=item.id,
            user_id=current_user.id,
            timestamp=datetime.utcnow(),
            change_description=f"Item updated by {current_user.username}"
        )
        db.session.add(change_log)
        
        # Save changes
        db.session.commit()
        flash("Inventory item updated successfully!", "success")
        return redirect(url_for('item_details', item_id=item.id))

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

@app.route("/inventory/checkout/<int:item_id>", methods=["POST"])
@login_required
def checkout_inventory(item_id):
    try:
        # Ensure we get the latest data
        db.session.expire_all()
        
        # Fetch the item and verify it exists
        item = Inventory.query.get_or_404(item_id)
        borrower_name = request.form.get("borrower_name")
        
        if not borrower_name:
            flash("Borrower name is required", "danger")
            return redirect(url_for("loaner_inventory"))
        
        # Check if item is a loaner
        if not item.is_loaner:
            flash(f"{item.asset_tag} is not a loaner device", "warning")
            return redirect(url_for("loaner_inventory"))
        
        # Direct SQL check for active checkouts to avoid caching issues
        active_checkouts = Checkout.query.filter_by(item_id=item.id, return_date=None).all()
        
        if active_checkouts:
            flash(f"{item.asset_tag} is already checked out", "warning")
            return redirect(url_for("loaner_inventory"))
        
        # Create the checkout record
        new_checkout = Checkout(
            user_id=current_user.id,
            item_id=item.id,
            borrower_name=borrower_name,
            checkout_date=datetime.utcnow()
        )
        
        # Add a log entry for the checkout
        log_entry = Log(
            action="Device Checkout",
            user=current_user.username,
            item_name=f"{item.asset_tag} ({item.asset_type})",
            timestamp=datetime.utcnow()
        )
        
        db.session.add(new_checkout)
        db.session.add(log_entry)
        db.session.commit()
        
        # Verify the checkout was created
        verify_checkout = Checkout.query.filter_by(id=new_checkout.id).first()
        if verify_checkout:
            flash(f"{item.asset_tag} checked out to {borrower_name}", "success")
        else:
            flash("Checkout failed - please try again", "danger")
            
    except Exception as e:
        db.session.rollback()
        flash(f"Error during checkout: {str(e)}", "danger")
        
    return redirect(url_for("loaner_inventory"))

@app.route("/inventory/return/<int:checkout_id>", methods=["POST"])
@login_required
def return_inventory(checkout_id):
    try:
        # Ensure we get the latest data
        db.session.expire_all()
        
        checkout = Checkout.query.get_or_404(checkout_id)
        if checkout.return_date is None:
            # Get item info before committing
            item_tag = checkout.inventory_item.asset_tag
            item_type = checkout.inventory_item.asset_type
            borrower = checkout.borrower_name
            
            # Set return date
            checkout.return_date = datetime.utcnow()
            
            # Add a log entry for the return
            log_entry = Log(
                action="Device Return",
                user=current_user.username,
                item_name=f"{item_tag} ({item_type})",
                timestamp=datetime.utcnow()
            )
            db.session.add(log_entry)
            db.session.commit()
            
            flash(f"{item_tag} returned successfully from {borrower}", "success")
        else:
            flash("Item is already returned", "warning")
    
    except Exception as e:
        db.session.rollback()
        flash(f"Error during check-in: {str(e)}", "danger")
        
    return redirect(url_for("loaner_inventory"))

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

#@app.route('/loaner_inventory')
# @login_required
#def loaner_inventory():
  #  loaners = Inventory.query.filter_by(is_loaner=True).all()  # Get all loaners
  #  return render_template('loaner_inventory.html', loaners=loaners)

@app.route("/inventory/loaners")
@login_required
def loaner_inventory():
    # Clear any cached data
    db.session.expire_all()
    
    # Get all loaner items with a fresh query that includes their active checkouts
    loaners = Inventory.query.filter_by(is_loaner=True).all()
    
    # For each loaner, directly query its active checkouts to bypass any caching
    loaner_with_status = []
    for item in loaners:
        # Get active checkouts directly from database
        active_checkouts = Checkout.query.filter_by(
            item_id=item.id, 
            return_date=None
        ).order_by(Checkout.checkout_date.desc()).all()
        
        # First active checkout or None
        active_checkout = active_checkouts[0] if active_checkouts else None
        
        loaner_with_status.append({
            'item': item,
            'active_checkout': active_checkout,
            'is_checked_out': bool(active_checkout)
        })
    
    return render_template(
        "loaner_inventory.html", 
        loaners=loaners,
        loaner_with_status=loaner_with_status
    )

@app.route("/inventory/loaner-history")
@login_required
def loaner_history():
    # Query all checkouts for loaner items
    checkouts = Checkout.query\
        .join(Inventory, Checkout.item_id == Inventory.id)\
        .filter(Inventory.is_loaner == True)\
        .order_by(Checkout.checkout_date.desc())\
        .all()
    
    return render_template("loaner_history.html", checkouts=checkouts)
