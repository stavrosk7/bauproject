from datetime import datetime
from extensions import db

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    assignments = db.relationship('ProjectAssignment', backref='project', lazy=True)
    reports = db.relationship('Report', backref='project', lazy=True)

class ProjectAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    engineer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow) 