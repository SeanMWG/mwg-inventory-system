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
    submit = SubmitField('Add Inventory')

class CheckoutForm(FlaskForm):
    user_name = StringField('User Name', validators=[DataRequired()])  # ✅ Store username instead of ID
    submit = SubmitField('Check Out')

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
