# Report business logic will be placed here 

from model.report import Report, Photo
from model.project import ProjectAssignment
from model.user import User
from utils.security import allowed_file
from werkzeug.utils import secure_filename
from flask import current_app
import uuid, os
from datetime import datetime

def get_project_reports(project_id, report_type, manager_id):
    from model.project import Project
    project = Project.query.get_or_404(project_id)
    if project.manager_id != manager_id:
        return None
    reports = Report.query.filter_by(project_id=project_id, report_type=report_type).all()
    return reports

def submit_report(project_id, report_type, description, latitude, longitude, photo_file, engineer_id):
    # Verify project assignment
    from model.project import ProjectAssignment
    if not ProjectAssignment.query.filter_by(project_id=project_id, engineer_id=engineer_id).first():
        return False, 'Unauthorized'
    # Create report
    report = Report(
        project_id=project_id,
        report_type=report_type,
        description=description,
        latitude=latitude,
        longitude=longitude
    )
    from model.user import db
    db.session.add(report)
    db.session.flush()  # Get report ID
    # Save photo
    if photo_file and allowed_file(photo_file.filename):
        filename = secure_filename(f"{uuid.uuid4()}_{photo_file.filename}")
        photo_file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        photo_record = Photo(
            report_id=report.id,
            filename=filename
        )
        db.session.add(photo_record)
    db.session.commit()
    return True, report 