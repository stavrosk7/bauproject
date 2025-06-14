# Project business logic will be placed here 

from model.project import Project, ProjectAssignment
from model.user import User
from model.report import Report
from utils.security import hash_password
from flask import jsonify

def create_project(name, description, manager_id):
    project = Project(
        name=name,
        description=description,
        manager_id=manager_id
    )
    return project

def get_available_engineers(project_id, manager_id):
    # Get all engineers created by this manager
    engineers = User.query.filter_by(created_by=manager_id, is_manager=False).all()
    # Get currently assigned engineers for this project
    assigned_engineers = ProjectAssignment.query.filter_by(project_id=project_id).all()
    assigned_engineer_ids = [assignment.engineer_id for assignment in assigned_engineers]
    # Filter out already assigned engineers
    available_engineers = [engineer for engineer in engineers if engineer.id not in assigned_engineer_ids]
    return available_engineers

def assign_engineers(project_id, engineer_ids, manager_id):
    # Verify that all engineers were created by this manager
    engineers = User.query.filter(
        User.id.in_(engineer_ids),
        User.created_by == manager_id,
        User.is_manager == False
    ).all()
    if len(engineers) != len(engineer_ids):
        return False, 'Invalid engineer selection'
    # Remove existing assignments
    ProjectAssignment.query.filter_by(project_id=project_id).delete()
    # Create new assignments
    for engineer in engineers:
        assignment = ProjectAssignment(project_id=project_id, engineer_id=engineer.id)
        from model.user import db
        db.session.add(assignment)
    try:
        from model.user import db
        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        return False, str(e) 