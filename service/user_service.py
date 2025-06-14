# User business logic will be placed here 

from model.user import User
from model.project import ProjectAssignment
from utils.security import hash_password, verify_password
from flask_login import login_user
from flask import flash

def register_user(username, password, subscription, first_name=None, last_name=None, phone=None, card_token=None):
    user = User(
        username=username,
        password_hash=hash_password(password),
        is_manager=True,
        subscription_id=subscription.id,
        card_token=card_token,
        first_name=first_name,
        last_name=last_name,
        phone=phone
    )
    return user

def login_user_service(user, password):
    if user and verify_password(user.password_hash, password):
        login_user(user)
        return True
    return False

def create_engineer(username, password, manager_id):
    user = User(
        username=username,
        password_hash=hash_password(password),
        is_manager=False,
        created_by=manager_id
    )
    return user

def check_subscription_limits(user):
    if not user.subscription:
        return False
    if user.subscription.max_projects != -1:
        project_count = len(user.projects)
        if project_count >= user.subscription.max_projects:
            return False
    if user.subscription.max_engineers != -1:
        engineer_count = len({a.engineer_id for p in user.projects for a in p.assignments})
        if engineer_count >= user.subscription.max_engineers:
            return False
    return True 