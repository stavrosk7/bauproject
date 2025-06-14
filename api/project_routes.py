# Project-related API routes will be placed here 

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session, current_app
from flask_login import login_required, current_user
from service.project_service import get_available_engineers, assign_engineers, create_project
from service.report_service import get_project_reports, submit_report as submit_report_service
from model.user import User, db
from model.project import Project, ProjectAssignment
from model.report import Report, Photo
from utils.security import allowed_file
from werkzeug.utils import secure_filename
import uuid, os
from service.user_service import check_subscription_limits
from service.project_service import create_project as create_project_service
from service.user_service import create_engineer as create_engineer_service

project_api = Blueprint('project_api', __name__)

@project_api.route('/api/project/<int:project_id>/available-engineers')
@login_required
def api_get_available_engineers(project_id):
    available_engineers = get_available_engineers(project_id, current_user.id)
    return jsonify([
        {'id': e.id, 'username': e.username} for e in available_engineers
    ])

@project_api.route('/api/project/<int:project_id>/assign-engineers', methods=['POST'])
@login_required
def api_assign_engineers(project_id):
    data = request.get_json()
    engineer_ids = data.get('engineers', [])
    success, error = assign_engineers(project_id, engineer_ids, current_user.id)
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': error}), 400

@project_api.route('/api/project/<int:project_id>/reports/<string:report_type>')
@login_required
def api_get_project_reports(project_id, report_type):
    reports = get_project_reports(project_id, report_type, current_user.id)
    if reports is None:
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify([
        {
            'id': r.id,
            'description': r.description,
            'created_at': r.created_at.isoformat(),
            'latitude': r.latitude,
            'longitude': r.longitude,
            'photos': [
                {'id': p.id, 'filename': p.filename, 'uploaded_at': p.uploaded_at.isoformat()} for p in r.photos
            ]
        } for r in reports
    ])

@project_api.route('/submit_report', methods=['GET', 'POST'])
@login_required
def api_submit_report():
    if current_user.is_manager:
        return jsonify({'error': 'Unauthorized'}), 403
    if request.method == 'POST':
        project_id = request.form.get('project_id')
        report_type = request.form.get('report_type', 'progress')
        description = request.form.get('description')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        photo = request.files.get('photo')
        success, result = submit_report_service(project_id, report_type, description, latitude, longitude, photo, current_user.id)
        if not success:
            flash(result)
            return redirect(url_for('project_api.dashboard'))
        flash('Report submitted successfully')
        return redirect(url_for('project_api.dashboard'))
    project_id = request.args.get('project_id')
    return render_template('submit_report.html', project_id=project_id)

@project_api.route('/dashboard')
def dashboard():
    from model.project import Project, ProjectAssignment
    if current_user.is_manager:
        projects = Project.query.filter_by(manager_id=current_user.id).all()
        return render_template('manager_dashboard.html', projects=projects)
    else:
        assignments = ProjectAssignment.query.filter_by(engineer_id=current_user.id).all()
        return render_template('engineer_dashboard.html', assignments=assignments)

@project_api.route('/create_project', methods=['POST'])
@login_required
def create_project():
    if not current_user.is_manager:
        return jsonify({'error': 'Unauthorized'}), 403
    if not check_subscription_limits(current_user):
        flash('You have reached your subscription limits')
        return redirect(url_for('project_api.dashboard'))
    name = request.form.get('name')
    description = request.form.get('description')
    project = create_project_service(name, description, current_user.id)
    db.session.add(project)
    db.session.commit()
    flash('Project created successfully')
    return redirect(url_for('project_api.dashboard'))

@project_api.route('/create_engineer', methods=['POST'])
@login_required
def create_engineer():
    if not current_user.is_manager:
        return jsonify({'error': 'Unauthorized'}), 403
    if not check_subscription_limits(current_user):
        flash('You have reached your subscription limits')
        return redirect(url_for('project_api.dashboard'))
    username = request.form.get('username')
    password = request.form.get('password')
    if User.query.filter_by(username=username).first():
        flash('Username already exists')
        return redirect(url_for('project_api.dashboard'))
    user = create_engineer_service(username, password, current_user.id)
    db.session.add(user)
    db.session.commit()
    flash('Engineer account created successfully')
    return redirect(url_for('project_api.dashboard'))

@project_api.route('/api/project/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    if not current_user.is_manager:
        return jsonify({'error': 'Unauthorized'}), 403
    
    project = Project.query.get_or_404(project_id)
    if project.manager_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        # Delete all photos associated with the project's reports
        for report in project.reports:
            for photo in report.photos:
                try:
                    photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.filename)
                    if os.path.exists(photo_path):
                        os.remove(photo_path)
                except Exception as e:
                    print(f"Error deleting photo file: {e}")
                db.session.delete(photo)
            db.session.delete(report)
        
        # Delete project assignments
        ProjectAssignment.query.filter_by(project_id=project.id).delete()
        
        # Delete the project
        db.session.delete(project)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@project_api.route('/api/engineer/<int:engineer_id>/delete', methods=['POST'])
@login_required
def delete_engineer(engineer_id):
    if not current_user.is_manager:
        return jsonify({'error': 'Unauthorized'}), 403
    
    engineer = User.query.get_or_404(engineer_id)
    if engineer.created_by != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        # Delete all photos associated with the engineer's reports
        for assignment in engineer.assigned_projects:
            for report in assignment.project.reports:
                if report.engineer_id == engineer.id:
                    for photo in report.photos:
                        try:
                            photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.filename)
                            if os.path.exists(photo_path):
                                os.remove(photo_path)
                        except Exception as e:
                            print(f"Error deleting photo file: {e}")
                        db.session.delete(photo)
                    db.session.delete(report)
        
        # Delete project assignments
        ProjectAssignment.query.filter_by(engineer_id=engineer.id).delete()
        
        # Delete the engineer
        db.session.delete(engineer)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@project_api.route('/api/engineers')
@login_required
def get_engineers():
    if not current_user.is_manager:
        return jsonify({'error': 'Unauthorized'}), 403
    
    engineers = User.query.filter_by(created_by=current_user.id, is_manager=False).all()
    return jsonify([{
        'id': engineer.id,
        'username': engineer.username
    } for engineer in engineers])

# Θα προστεθούν και τα υπόλοιπα project/engineer/report endpoints εδώ 