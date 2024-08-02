#!/usr/bin/env python3
"""All routes for admin CRUD operations"""
from flask import Blueprint, request, jsonify, url_for, current_app
from bson.objectid import ObjectId
from app import mail
from app.models.admin import Admin
from pymongo.errors import PyMongoError
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import uuid
import logging

admin_bp = Blueprint('admin', __name__)

adminsCollection = current_app.adminsCollection

# In-memory store for reset tokens
reset_tokens = {}

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)

def send_email(subject, recipients, body):
    msg = Message(subject=subject, recipients=recipients, body=body)
    try:
        mail.send(msg)
        logging.debug(f"Email sent to {recipients}")
    except Exception as e:
        logging.error(f"Failed to send email to {recipients}: {e}")

# Create admin Account
@admin_bp.route('/api/admin/admins', methods=['POST', 'OPTIONS'])
def create_admin():
    """create admin as instance of admin.
       post admin to mongodb database.
       Return: "msg": "admin created successfully"
       and success status
    """
    data = request.json
    try:
        admin = Admin(
            name=data['name'],
            password=generate_password_hash(data['password']),
            dob=data['DoB'],
            sex=data['sex'],
            contact_details=data['contactDetails'],
            emergency_contact=data['emergencyContact'],
            role=data['role']
        )
    except KeyError as e:
        return jsonify({"error": f"Missing field {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    try:
        insert_result = adminsCollection.insert_one(admin.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    admin_id = insert_result.inserted_id

    # Send notification email with a reset password link
    email = data['contactDetails']['email']
    reset_token = str(uuid.uuid4())
    reset_tokens[reset_token] = email
    reset_url = url_for('main.admin.reset_password', token=reset_token, _external=True)
    email_body = f"Dear {data['name']['fname']},\n\nYour admin account has been created successfully. Please use the following link to set your password: {reset_url}\n\nThank you."
    send_email("Admin Account Created", [email], email_body)

    return jsonify({"msg": "admin created successfully", "adminId": str(admin_id)}), 201

# Get all admins
@admin_bp.route('/api/admin/admins', methods=['GET', 'OPTIONS'])
def get_all_admins():
    """find all admins fron mongodb and
    return list of all the admins
    """
    try:
        admins = adminsCollection.find({"active": True})
        admins_list = [{
            "adminId": str(admin['_id']),
            "dateCreated": admin['date_created'],
            "fname": admin['name']['fname'],
            "lname": admin['name']['lname'],
            "sex": admin['sex'],
            "DoB": admin['dob'],
            "phone": admin['contact_details']['phone'],
            "email": admin['contact_details']['email'],
            "address": admin['contact_details']['address'],
            "emergencyContactName": admin['emergency_contact']['name'],
            "emergencyContactPhone": admin['emergency_contact']['phone'],
            "emergencyContactAddress": admin['emergency_contact']['address'],
        } for admin in admins]
        return jsonify(admins_list), 200
    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500

# Get a Specific admin Details
@admin_bp.route('/api/admin/admins/<admin_id>', methods=['GET', 'OPTIONS'])
def get_admin(admin_id):
    try:
        admin = adminsCollection.find_one(
            {"_id": ObjectId(admin_id), "active": True}
        )
        if admin:
            return jsonify({
                "adminId": str(admin['_id']),
                "dateCreated": admin['date_created'],
                "fname": admin['name']['fname'],
                "lname": admin['name']['lname'],
                "sex": admin['sex'],
                "DoB": admin['dob'],
                "phone": admin['contact_details']['phone'],
                "email": admin['contact_details']['email'],
                "address": admin['contact_details']['address'],
                "emergencyContactName": admin['emergency_contact']['name'],
                "emergencyContactPhone": admin['emergency_contact']['phone'],
                "emergencyContactAddress": admin['emergency_contact']['address']
            }), 200
        else:
            return jsonify({"error": "admin not found"}), 404
    except InvalidId:
        return jsonify({"error": "Invalid admin ID format"}), 404
    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Update Specific admin Details
@admin_bp.route('/api/admin/admins/<admin_id>', methods=['PUT', 'OPTIONS'])
def update_admin(admin_id):
    """update a specific admin with a admin_id.
    Args:
        admin_id  (str): admin unique id
    """
    data = request.json
    try:
        update_data = {
            "name": data['name'],
            "dob": data['DoB'],
            "sex": data['sex'],
            "contact_details": data['contactDetails'],
            "emergency_contact": data['emergencyContact'],
        }
    except KeyError as e:
        return jsonify({"error": f"Missing field {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    try:
        result = adminsCollection.update_one(
            {"_id": ObjectId(admin_id)}, {"$set": update_data}
        )
        if result.matched_count == 0:
            return jsonify({"msg": "admin not found"}), 404
        return jsonify({"msg": "admin updated successfully"}), 200
    except InvalidId:
        return jsonify({"error": "Invalid admin ID format"}), 400
    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500

# Deactivate/Delete admin Account
@admin_bp.route('/api/admin/admins/<admin_id>', methods=['DELETE', 'OPTIONS'])
@jwt_required()
def delete_admin(admin_id):
    """update a specific admin with a admin_id.
    setting the active attribute to False
    Args:
        admin_id  (str): admin unique id
    """
    try:
        result = adminsCollection.update_one(
            {"_id": ObjectId(admin_id)}, {"$set": {"active": False}}
        )
        if result.matched_count:
            return jsonify({"msg": "admin deactivated"}), 204
        return jsonify({"error": "admin not found"}), 404
    except InvalidId:
        return jsonify({"error": "Invalid admin ID format"}), 400
    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500

# Forgot Password
@admin_bp.route('/api/admin/forgot_password', methods=['POST', 'OPTIONS'])
def forgot_password():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({"msg": "Missing email"}), 400
    
    user = adminsCollection.find_one({"contact_details.email": email})
    if not user:
        return jsonify({"msg": "Email not found"}), 404
    
    reset_token = str(uuid.uuid4())
    reset_tokens[reset_token] = email
    reset_url = url_for('admin.reset_password', token=reset_token, _external=True)
    
    msg = Message(subject="Password Reset Request",
                  recipients=[email],
                  body=f'Reset your password using the following link: {reset_url}')
    try:
        mail.send(msg)
        return jsonify({"msg": "Password Reset email sent"}), 200
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {str(e)}")
        return jsonify({"msg": f"Failed to send email: {str(e)}"}), 500

# Reset Password
@admin_bp.route('/api/admin/reset_password/<token>', methods=['POST', 'OPTIONS'])
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
    
    user = adminsCollection.find_one({"contact_details.email": email})
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    new_hashed_password = generate_password_hash(new_password)
    adminsCollection.update_one({"contact_details.email": email}, {"$set": {"password": new_hashed_password}})
    
    del reset_tokens[token]  # Invalidate the token after use
    
    return jsonify({"msg": "Password has been reset"}), 200
