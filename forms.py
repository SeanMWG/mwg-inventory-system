from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField, BooleanField, SubmitField, IntegerField, TextAreaField, DateField
from wtforms.validators import DataRequired, Length, Optional

class InventoryForm(FlaskForm):
    site_name = StringField('Site Name', validators=[DataRequired()])
    room_number = StringField('Room Number', validators=[Optional()])
    room_name = StringField('Room Name', validators=[Optional()])
    asset_tag = StringField('Asset Tag', validators=[DataRequired()])
    asset_type = StringField('Asset Type', validators=[DataRequired()])
    model = StringField('Model', validators=[Optional()])
    serial_number = StringField('Serial Number', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    assigned_to = StringField('Assigned To', validators=[Optional()])
    date_assigned = DateField('Date Assigned', format='%Y-%m-%d', validators=[Optional()])
    date_decommissioned = DateField('Date Decommissioned', format='%Y-%m-%d', validators=[Optional()])
    is_loaner = BooleanField('Loaner Item?')  # ✅ Added Loaner Field
    submit = SubmitField('Add Inventory')

class CheckoutForm(FlaskForm):
    borrower_name = StringField("Borrower's Name", validators=[DataRequired()])
    checkout_date = DateField("Checkout Date", format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField("Check Out Item")

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    role = SelectField('Role', choices=[('Admin', 'Admin'), ('Editor', 'Editor'), ('Reader', 'Reader')], validators=[DataRequired()])
    submit = SubmitField('Add User')

class UpdateUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=100)])
    password = PasswordField('New Password (leave blank to keep current)', validators=[Length(min=6)])
    role = SelectField('Role', choices=[('Admin', 'Admin'), ('Editor', 'Editor'), ('Reader', 'Reader')], validators=[DataRequired()])
    submit = SubmitField('Update User')

class AddInventoryForm(FlaskForm):
    site_name = StringField('Site Name', validators=[DataRequired()])
    room_number = StringField('Room Number', validators=[Optional()])
    room_name = StringField('Room Name', validators=[Optional()])
    asset_tag = StringField('Asset Tag', validators=[DataRequired()])
    asset_type = StringField('Asset Type', validators=[DataRequired()])
    model = StringField('Model', validators=[Optional()])
    serial_number = StringField('Serial Number', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    assigned_to = StringField('Assigned To', validators=[Optional()])
    date_assigned = DateField('Date Assigned', format='%Y-%m-%d', validators=[Optional()])
    date_decommissioned = DateField('Date Decommissioned', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Add Inventory')

class EditInventoryForm(FlaskForm):
    site_name = StringField('Site Name', validators=[DataRequired()])
    asset_tag = StringField('Asset Tag', validators=[DataRequired()])
    asset_type = StringField('Asset Type', validators=[DataRequired()])
    model = StringField('Model', validators=[DataRequired()])
    serial_number = StringField('Serial Number', validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional()])
    
    submit = SubmitField('Update Inventory')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Update Password')
