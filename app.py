#!/usr/bin/env python3
"""
app.py

A simple Payment Receipts web app using Flask, Flask-Login, Flask-WTF, and SQLite.

Features (MVP):
1. User registration & login (username/password).
2. Create, view, search, edit, delete receipts.
3. Export a single receipt as PDF.
4. Backup all receipts as JSON.

High-school level: clear docstrings and comments throughout.
"""

import os
import io
import json
from datetime import datetime
from flask import (Flask, render_template, redirect,
                   url_for, request, flash, send_file)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (LoginManager, UserMixin,
                         login_user, login_required,
                         logout_user, current_user)
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, DecimalField,
                     DateField, SubmitField)
from wtforms.validators import DataRequired, Length, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from reportlab.pdfgen import canvas

# ------------------------------------------------------------------------------
# App & Database Initialization
# ------------------------------------------------------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # CHANGE in production!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///receipts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------------------------------------------------------------------
# Login Manager Setup
# ------------------------------------------------------------------------------
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# ------------------------------------------------------------------------------
# Models
# ------------------------------------------------------------------------------
class User(UserMixin, db.Model):
    """
    User model for authentication.

    Attributes:
        id (int): Primary key.
        username (str): Unique username.
        password_hash (str): Hashed password.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password: str):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Return True if password matches stored hash."""
        return check_password_hash(self.password_hash, password)


class Receipt(db.Model):
    """
    Receipt model represents a payment receipt.

    Attributes:
        id (int): Primary key.
        amount (Decimal): Payment amount.
        date (date): Payment date.
        payer (str): Who paid.
        payee (str): Who received payment.
        purpose (str): Reason for payment.
        user_id (int): Owner (foreign key to User.id).
    """
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.Date, nullable=False)
    payer = db.Column(db.String(100), nullable=False)
    payee = db.Column(db.String(100), nullable=False)
    purpose = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# ------------------------------------------------------------------------------
# Forms
# ------------------------------------------------------------------------------
class RegistrationForm(FlaskForm):
    """Form for new users to register."""
    username = StringField('Username',
                           validators=[DataRequired(), Length(3, 80)])
    password = PasswordField('Password', validators=[DataRequired(), Length(6)])
    confirm = PasswordField('Confirm Password',
                            validators=[DataRequired(),
                                        EqualTo('password',
                                        message='Passwords must match')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    """Form for existing users to log in."""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class ReceiptForm(FlaskForm):
    """Form to create or edit a receipt."""
    amount = DecimalField('Amount', places=2, validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()],
                     format='%Y-%m-%d')
    payer = StringField('Payer', validators=[DataRequired(),
                                             Length(1, 100)])
    payee = StringField('Payee', validators=[DataRequired(),
                                             Length(1, 100)])
    purpose = StringField('Purpose', validators=[DataRequired(),
                                                 Length(1, 200)])
    submit = SubmitField('Save')


# ------------------------------------------------------------------------------
# User Loader for Flask-Login
# ------------------------------------------------------------------------------
@login_manager.user_loader
def load_user(user_id: str):
    """Given user_id, return the associated User object."""
    return User.query.get(int(user_id))


# ------------------------------------------------------------------------------
# Routes: Auth
# ------------------------------------------------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Register a new user.
    - GET: show registration form.
    - POST: validate & create user, then redirect to login.
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.', 'danger')
        else:
            user = User(username=form.username.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Log in an existing user.
    - GET: show login form.
    - POST: check credentials, log in, redirect to receipt list.
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('list_receipts'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """Log out the current user."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# ------------------------------------------------------------------------------
# Routes: Receipts CRUD
# ------------------------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
@app.route('/receipts', methods=['GET', 'POST'])
@login_required
def list_receipts():
    """
    List and search receipts.
    - GET: show all receipts for current user.
    - POST: filter by date, payer, or amount partial match.
    """
    query = Receipt.query.filter_by(user_id=current_user.id)
    # Simple search
    if request.method == 'POST':
        search_term = request.form.get('search', '').strip()
        if search_term:
            # filter by payer or payee
            query = query.filter(
                (Receipt.payer.ilike(f'%{search_term}%')) |
                (Receipt.payee.ilike(f'%{search_term}%'))
            )
    receipts = query.order_by(Receipt.date.desc()).all()
    return render_template('receipts.html', receipts=receipts)


@app.route('/receipts/create', methods=['GET', 'POST'])
@login_required
def create_receipt():
    """
    Create a new receipt.
    - GET: show blank form.
    - POST: validate & save, then redirect to list.
    """
    form = ReceiptForm()
    if form.validate_on_submit():
        r = Receipt(
            amount=form.amount.data,
            date=form.date.data,
            payer=form.payer.data,
            payee=form.payee.data,
            purpose=form.purpose.data,
            user_id=current_user.id
        )
        db.session.add(r)
        db.session.commit()
        flash('Receipt created.', 'success')
        return redirect(url_for('list_receipts'))
    return render_template('form.html', form=form, action='Create Receipt')


@app.route('/receipts/edit/<int:rid>', methods=['GET', 'POST'])
@login_required
def edit_receipt(rid: int):
    """
    Edit an existing receipt by ID.
    - GET: populate form with existing data.
    - POST: validate & update, then redirect.
    """
    r = Receipt.query.get_or_404(rid)
    if r.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('list_receipts'))

    form = ReceiptForm(obj=r)
    if form.validate_on_submit():
        form.populate_obj(r)
        db.session.commit()
        flash('Receipt updated.', 'success')
        return redirect(url_for('list_receipts'))
    return render_template('form.html', form=form, action='Edit Receipt')


@app.route('/receipts/delete/<int:rid>', methods=['POST'])
@login_required
def delete_receipt(rid: int):
    """
    Delete a receipt by ID.
    - POST only.
    """
    r = Receipt.query.get_or_404(rid)
    if r.user_id != current_user.id:
        flash('Access denied.', 'danger')
    else:
        db.session.delete(r)
        db.session.commit()
        flash('Receipt deleted.', 'info')
    return redirect(url_for('list_receipts'))


# ------------------------------------------------------------------------------
# Route: Export single receipt as PDF
# ------------------------------------------------------------------------------
@app.route('/receipts/<int:rid>/download')
@login_required
def download_receipt(rid: int):
    """
    Generate and send a PDF for a single receipt.
    Uses ReportLab to draw text onto a canvas in memory.
    """
    r = Receipt.query.get_or_404(rid)
    if r.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('list_receipts'))

    # Create PDF in memory
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setTitle(f"Receipt_{rid}")
    p.drawString(100, 800, f"Receipt ID: {rid}")
    p.drawString(100, 780, f"Date: {r.date.strftime('%Y-%m-%d')}")
    p.drawString(100, 760, f"Amount: ${r.amount}")
    p.drawString(100, 740, f"Payer: {r.payer}")
    p.drawString(100, 720, f"Payee: {r.payee}")
    p.drawString(100, 700, f"Purpose: {r.purpose}")
    p.showPage()
    p.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"receipt_{rid}.pdf",
        mimetype='application/pdf'
    )


# ------------------------------------------------------------------------------
# Route: Backup all receipts as JSON
# ------------------------------------------------------------------------------
@app.route('/backup')
@login_required
def backup():
    """
    Export all current user's receipts as a JSON file.
    """
    receipts = Receipt.query.filter_by(user_id=current_user.id).all()
    data = []
    for r in receipts:
        data.append({
            'id': r.id,
            'amount': float(r.amount),
            'date': r.date.isoformat(),
            'payer': r.payer,
            'payee': r.payee,
            'purpose': r.purpose
        })
    json_str = json.dumps(data, indent=2)
    buffer = io.BytesIO(json_str.encode('utf-8'))
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name='receipts_backup.json',
        mimetype='application/json'
    )


# ------------------------------------------------------------------------------
# Initialize Database (create tables)
# ------------------------------------------------------------------------------
@app.before_first_request
def create_tables():
    """Create database tables if not already present."""
    db.create_all()


# ------------------------------------------------------------------------------
# Run the App
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    # Using debug=True only for development; turn off in production!
    app.run(debug=True)
