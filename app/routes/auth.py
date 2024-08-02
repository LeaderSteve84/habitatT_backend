#!/usr/bin/env python3
"""All routes for tenant CRUD operations"""
from flask import Blueprint, request, jsonify, url_for, current_app
from flask_jwt_extended import create_access_token, jwt_required, set_access_cookies, unset_jwt_cookies, get_jwt
from flask_mail import Message, Mail
from werkzeug.security import generate_password_hash, check_password_hash
from app import mail
import datetime
import uuid
import logging

auth_bp = Blueprint('auth_bp', __name__)
reset_tokens = {}
revoked_tokens = set()  # Move this to a shared location if needed

tenantsCollection = current_app.tenantsCollection
adminsCollection = current_app.adminsCollection

# Utility functions
def authenticate(email, password, role):
    email = email.strip().lower()
    logging.debug(f"Authenticating user with email: {email} and role: {role}")
    
    if role == 'admin':
        user = adminsCollection.find_one({"contact_details.email": email})
    elif role == 'tenant':
        user = tenantsCollection.find_one({"contact_details.email": email})
    else:
        logging.debug("Invalid role provided")
        return None
    
    if user and check_password_hash(user["password"], password):
        logging.debug("Password match!")
        return user
    
    logging.debug("Authentication failed!")
    return None

@auth_bp.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if not request.is_json:
        logging.debug("Request missing JSON")
        return jsonify({"msg": "Missing JSON in request"}), 400

    data = request.get_json()

    email = data.get('email').strip().lower() if data.get('email') else None
    password = data.get('password')
    role = data.get('role')
    remember_me = data.get('remember_me', False)
    
    if not email or not password or not role:
        logging.debug("Missing email, password, or role")
        return jsonify({"msg": "Missing email, password, or role"}), 400
    
    user = authenticate(email, password, role)
    
    if not user:
        logging.debug("Authentication failed")
        return jsonify({"msg": "Invalid email, password, or role"}), 401
    
    if role == 'tenant' and not user.get('active', False):
        logging.debug("Tenant account is not active")
        return jsonify({"msg": "Account is not active"}), 403
    
    expires = datetime.timedelta(days=7) if remember_me else datetime.timedelta(hours=1)
    access_token = create_access_token(identity={"email": email, "role": role}, expires_delta=expires)
    response = jsonify(msg="You have successfully logged in", access_token=access_token)
    set_access_cookies(response, access_token)

    logging.debug("User authenticated successfully")
    return response


@auth_bp.route('/api/forgot_password', methods=['POST', 'OPTIONS'])
def forgot_password():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"msg": "Missing email"}), 400
    
    user = tenantsCollection.find_one({"contact_details.email": email}) or adminsCollection.find_one({"contact_details.email": email})
    if not user:
        return jsonify({"msg": "Email not found"}), 404
    
    reset_token = str(uuid.uuid4())
    reset_tokens[reset_token] = email
    reset_url = url_for('main.auth_bp.reset_password', token=reset_token, _external=True)
    
    logging.debug(f"Reset token: {reset_token}")
    
    msg = Message(subject="Password Reset Request",
                  recipients=[email],
                  body=f'Reset your password using the following link: {reset_url}')
    try:
        mail.send(msg)
        return jsonify({"msg": "Password Reset email sent"}), 200
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {str(e)}")
        return jsonify({"msg": f"Failed to send email: {str(e)}"}), 500

@auth_bp.route('/api/reset_password/<token>', methods=['POST', 'OPTIONS'])
def reset_password(token):
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    data = request.get_json()
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if not new_password or not confirm_password:
        return jsonify({"msg": "Missing new password or confirmation"}), 400

    if new_password != confirm_password:
        return jsonify({"msg": "Passwords do not match"}), 400

    email = reset_tokens.get(token)
    if not email:
        return jsonify({"msg": "Invalid or expired token"}), 400
    
    user = tenantsCollection.find_one({"contact_details.email": email}) or adminsCollection.find_one({"contact_details.email": email})
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    new_hashed_password = generate_password_hash(new_password)
    user_role = user.get('role')  # check user role

    logging.debug(f"Resseting password for user with role: {user_role}")

    if user_role not in ['tenant', 'admin']:
        return jsonify({"msg": "Invalid user role"}), 400

    collection = tenantsCollection if user.get('role') == 'tenant' else adminsCollection
    result = collection.update_one({"contact_details.email": email}, {"$set": {"password": new_hashed_password}})
    
    if result.modified_count == 1:
        logging.debug("Password updated successfully")
    else:
        logging.debug("Password update failed")

    del reset_tokens[token]  # Invalidate the token after use
    
    return jsonify({"msg": "Password has been reset"}), 200

@auth_bp.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    revoked_tokens.add(jti)
    response = jsonify({"msg": "Successfully logged out"})
    unset_jwt_cookies(response)
    return response

