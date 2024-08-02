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

profile_bp = Blueprint('profile_bp', __name__)
adminsCollection = current_app.adminsCollection
tenantsCollection = current_app.tenantsCollection

@profile_bp.route('/api/profile', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_profile():
    identity = get_jwt_identity()
    email = identity.get('email')
    role = identity.get('role')
    
    # Assuming you have separate collections for admins and tenants
    collection = tenantsCollection
    user = collection.find_one({"contact_details.email": email})
    
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    # Exclude sensitive fields if necessary before returning the user document
    profile_data = {
        "first_name": user["name"]["fname"],
        "last_name": user["name"]["lname"],
        "Date of Birth": user["dob"],
        "Sex": user["sex"],
        "email": user["contact_details"]["email"],
        "phone_number": user["contact_details"]["phone"],
        "address": user["contact_details"]["address"],
        "Rentage_fees": user["tenancy_info"]["fees"],
        "Rentage_Paid": user["tenancy_info"]["paid"],
        "Rentage_Date_Paid": user["tenancy_info"]["datePaid"],
        "Rentage_Start": user["tenancy_info"]["start"],
        "Rentage_Expires": user["tenancy_info"]["expires"],
        "role": user.get("role", role)  # Assuming role might differ in some cases
        # Add more fields as needed
    }
    
    return jsonify(profile_data), 200
