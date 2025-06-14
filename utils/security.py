from werkzeug.security import generate_password_hash, check_password_hash

# Security utilities (password hashing, token, etc) will be placed here 

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS 

def hash_password(password):
    return generate_password_hash(password)

def verify_password(password_hash, password):
    return check_password_hash(password_hash, password) 