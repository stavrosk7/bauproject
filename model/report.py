from datetime import datetime
from extensions import db

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    engineer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    report_type = db.Column(db.String(20), nullable=False)  # progress, damage, bills, supply
    description = db.Column(db.Text)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    photos = db.relationship('Photo', backref='report', lazy=True)

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow) 