# Authentication API routes will be placed here 
from flask import Blueprint, request, render_template, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, current_user
from model.user import User
from model.project import Project
from model.report import Report
from utils.security import hash_password, verify_password
from utils.iris import IRIS_IBAN, IRIS_BENEF, IRIS_BANK, IRIS_REASON_PREFIX
from service.user_service import register_user, login_user_service
from datetime import datetime

auth_api = Blueprint('auth_api', __name__)

@auth_api.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        subscription_type = request.form.get('subscription')
        card_token = request.form.get('card_token')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        from model.user import db, Subscription
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('auth_api.register'))
        subscription = Subscription.query.filter_by(name=subscription_type.capitalize()).first()
        if not subscription:
            flash('Invalid subscription plan')
            return redirect(url_for('auth_api.register'))
        # Pro: IRIS flow
        if subscription_type == 'pro':
            session['pending_registration'] = {
                'username': username,
                'password': password,
                'subscription_id': subscription.id,
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone
            }
            amount = f'{subscription.price:.2f}'
            reason = f'{IRIS_REASON_PREFIX}{username}'
            return render_template('iris_payment.html', iban=IRIS_IBAN, benef=IRIS_BENEF, bank=IRIS_BANK, amount=amount, reason=reason, username=username)
        # Free
        user = register_user(username, password, subscription, first_name=first_name, last_name=last_name, phone=phone)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful')
        return redirect(url_for('auth_api.login'))
    return render_template('register.html')

@auth_api.route('/iris_confirm', methods=['POST'])
def iris_confirm():
    reg = session.get('pending_registration')
    if not reg:
        flash('Registration data not found. Please try again.')
        return redirect(url_for('auth_api.register'))
    from model.user import db, Subscription
    user = User(
        username=reg['username'],
        password_hash=hash_password(reg['password']),
        is_manager=True,
        subscription_id=reg['subscription_id'],
        first_name=reg.get('first_name'),
        last_name=reg.get('last_name'),
        phone=reg.get('phone')
    )
    db.session.add(user)
    db.session.commit()
    session.pop('pending_registration', None)
    flash('Registration completed! Your account will be activated once the payment is confirmed.')
    return redirect(url_for('auth_api.login'))

@auth_api.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if login_user_service(user, password):
            return redirect(url_for('project_api.dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@auth_api.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth_api.login')) 