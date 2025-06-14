# Admin API routes will be placed here 
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, login_required, current_user
from model.user import User
from model.project import Project, ProjectAssignment
from model.report import Report, Photo
from datetime import datetime, timedelta
from utils.security import hash_password, verify_password
import os

admin_api = Blueprint('admin_api', __name__)

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required')
            return redirect(url_for('auth_api.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_api.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and verify_password(user.password_hash, password) and user.is_admin:
            login_user(user)
            return redirect(url_for('admin_api.admin_dashboard'))
        flash('Invalid admin credentials')
    return render_template('admin_login.html')

@admin_api.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    managers = User.query.filter_by(is_manager=True).all()
    return render_template('admin_dashboard.html', managers=managers)

@admin_api.route('/admin/manager/<int:manager_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_manager(manager_id):
    from model.user import db
    manager = User.query.get_or_404(manager_id)
    if not manager.is_manager:
        flash('Invalid manager ID')
        return redirect(url_for('admin_api.admin_dashboard'))
    try:
        projects = Project.query.filter_by(manager_id=manager_id).all()
        for project in projects:
            reports = Report.query.filter_by(project_id=project.id).all()
            for report in reports:
                photos = Photo.query.filter_by(report_id=report.id).all()
                for photo in photos:
                    try:
                        photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.filename)
                        if os.path.exists(photo_path):
                            os.remove(photo_path)
                    except Exception as e:
                        print(f"Error deleting photo file: {e}")
                    db.session.delete(photo)
                db.session.delete(report)
            project_engineers = User.query.filter_by(is_manager=False).join(
                ProjectAssignment, User.id == ProjectAssignment.engineer_id
            ).filter(ProjectAssignment.project_id == project.id).all()
            ProjectAssignment.query.filter_by(project_id=project.id).delete()
            for engineer in project_engineers:
                other_assignments = ProjectAssignment.query.filter(
                    ProjectAssignment.engineer_id == engineer.id,
                    ProjectAssignment.project_id != project.id
                ).first()
                if not other_assignments:
                    db.session.delete(engineer)
            db.session.delete(project)
        db.session.delete(manager)
        db.session.commit()
        flash('Manager and all associated data (projects, engineers, reports, and photos) have been deleted successfully')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting manager: {str(e)}')
        return redirect(url_for('admin_api.admin_dashboard'))
    return redirect(url_for('admin_api.admin_dashboard'))

@admin_api.route('/admin/manager/<int:manager_id>/update_payment', methods=['POST'])
@login_required
@admin_required
def update_payment_status(manager_id):
    from model.user import db
    manager = User.query.get_or_404(manager_id)
    if not manager.is_manager:
        flash('Invalid manager ID')
        return redirect(url_for('admin_api.admin_dashboard'))
    payment_status = request.form.get('payment_status')
    if payment_status not in ['pending', 'paid', 'overdue']:
        flash('Invalid payment status')
        return redirect(url_for('admin_api.admin_dashboard'))
    manager.payment_status = payment_status
    if payment_status == 'paid':
        manager.last_payment_date = datetime.utcnow()
        if manager.subscription and manager.subscription.name == 'Pro':
            manager.next_payment_date = datetime.utcnow() + timedelta(days=30)
    db.session.commit()
    flash('Payment status updated successfully')
    return redirect(url_for('admin_api.admin_dashboard')) 