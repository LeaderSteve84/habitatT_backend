#!/usr/bin/env python3
"""All routes for tenant CRUD operations"""
from flask import Blueprint, request, jsonify, url_for, current_app
from bson.objectid import ObjectId
from flask_mail import Message
from app.models.tenant import Tenant
from pymongo.errors import PyMongoError
from werkzeug.security import generate_password_hash
from bson.errors import InvalidId
import uuid
from flask_jwt_extended import jwt_required, get_jwt_identity


tenant_bp = Blueprint('tenant', __name__)
logger = current_app.logger
mail = current_app.mail
reset_tokens = {}
tenantsCollection = current_app.tenantsCollection

# Utility function to send emails
def send_email(subject, recipients, body):
    msg = Message(subject=subject, recipients=recipients, body=body)
    try:
        mail.send(msg)
        logger.debug(f"Email sent to {recipients}")
    except Exception as e:
        logger.error(f"Failed to send email to {recipients}: {e}")

# Create Tenant Account
@tenant_bp.route('/api/admin/tenants', methods=['POST', 'OPTIONS'])
@jwt_required()
def create_tenant():
    """Create tenant as instance of Tenant, post tenant to MongoDB database,
       and send notification email with a reset password link.
    """
    data = request.json
    try:
        # Check if a tenant with same email or phone number already exist
        if tenantsCollection.find_one({
            "$or": [
                {"contact_details.email": data['contactDetails']['email']},
                {"contact_details.phone": data['contactDetails']['phone']}
            ]
        }):
            return jsonify(
                {"error": "Tenant with same email or phone exist"}
            )

        tenant = Tenant(
            name=data['name'],
            password=generate_password_hash(data['password']),
            dob=data['DoB'],
            sex=data['sex'],
            contact_details=data['contactDetails'],
            emergency_contact=data['emergencyContact'],
            tenancy_info=data['tenancyInfo'],
            lease_agreement_details=data['leaseAgreementDetails'],
            role=data['role']
        )
    except KeyError as e:
        return jsonify({"error": f"Missing field {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    try:
        insert_result = tenantsCollection.insert_one(tenant.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    tenant_id = insert_result.inserted_id

    # Send notification email with a reset password link
    email = data['contactDetails']['email']
    reset_token = str(uuid.uuid4())
    reset_tokens[reset_token] = email
    reset_url = url_for('main.auth_bp.reset_password', token=reset_token, _external=True)
    email_body = f"Dear {data['name']['fname']},\n\nYour tenant account has been created successfully. Please use the following link to set your password: {reset_url}\n\nThank you."
    send_email("Tenant Account Created", [email], email_body)

    return jsonify({"msg": "Tenant created successfully", "tenantId": str(tenant_id)}), 201


# Get all tenants
@tenant_bp.route('/api/admin/tenants', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_all_tenants():
    """Find all tenants from MongoDB and return a list of all the tenants."""
    try:
        tenants = tenantsCollection.find({"active": True})
        tenants_list = [{
            "tenantId": str(tenant['_id']),
            "dateCreated": tenant['date_created'],
            "lastUpdated": tenant['date_updated'],
            "fname": tenant['name']['fname'],
            "lname": tenant['name']['lname'],
            "sex": tenant['sex'],
            "DoB": tenant['dob'],
            "phone": tenant['contact_details']['phone'],
            "email": tenant['contact_details']['email'],
            "address": tenant['contact_details']['address'],
            "rentageFee": tenant['tenancy_info']['fees'],
            "rentagePaid": tenant['tenancy_info']['paid'],
            "datePaid": tenant['tenancy_info']['datePaid'],
            "rantageStarted": tenant['tenancy_info']['start'],
            "rantageExpires": tenant['tenancy_info']['expires'],
            "rentageArrears": tenant['tenancy_info']['arrears'],
            "emergencyContactName": tenant['emergency_contact']['name'],
            "emergencyContactPhone": tenant['emergency_contact']['phone'],
            "emergencyContactAddress": tenant['emergency_contact']['address'],
            "leaseAgreementDetails": tenant['lease_agreement_details']
        } for tenant in tenants]
        return jsonify(tenants_list), 200
    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500


# Get a Specific Tenant Details
@tenant_bp.route('/api/admin/tenants/<tenant_id>', methods=['GET', 'OPTIONS'])
def get_tenant(tenant_id):
    try:
        tenant = tenantsCollection.find_one(
            {"_id": ObjectId(tenant_id), "active": True}
        )
        if tenant:
            return jsonify({
                "tenantId": str(tenant['_id']),
                "dateCreated": tenant['date_created'],
                "lastUpdated": tenant['date_updated'],
                "fname": tenant['name']['fname'],
                "lname": tenant['name']['lname'],
                "sex": tenant['sex'],
                "DoB": tenant['dob'],
                "phone": tenant['contact_details']['phone'],
                "email": tenant['contact_details']['email'],
                "address": tenant['contact_details']['address'],
                "rentageFee": tenant['tenancy_info']['fees'],
                "rentagePaid": tenant['tenancy_info']['paid'],
                "datePaid": tenant['tenancy_info']['datePaid'],
                "rantageStarted": tenant['tenancy_info']['start'],
                "rantageExpires": tenant['tenancy_info']['expires'],
                "rentageArrears": tenant['tenancy_info']['arrears'],
                "emergencyContactName": tenant['emergency_contact']['name'],
                "emergencyContactPhone": tenant['emergency_contact']['phone'],
                "emergencyContactAddress": tenant['emergency_contact']['address'],
                "lease_agreement_details": tenant['lease_agreement_details']
            }), 200
        else:
            return jsonify({"error": "Tenant not found"}), 404
    except InvalidId:
        return jsonify({"error": "Invalid tenant ID format"}), 404
    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Update Specific Tenant Details
@tenant_bp.route('/api/admin/tenants/<tenant_id>', methods=['PUT', 'OPTIONS'])
@jwt_required()
def update_tenant(tenant_id):
    """Update a specific tenant with a tenant_id.
    Args:
        tenant_id (str): tenant unique id
    """
    data = request.json
    try:
        update_data = {
            "date_updated": data['lastUpdated'],
            "name": data['name'],
            "dob": data['DoB'],
            "sex": data['sex'],
            "contact_details": data['contactDetails'],
            "emergency_contact": data['emergencyContact'],
            "tenancy_info": data['tenancyInfo'],
            "lease_agreement_details": data['leaseAgreementDetails']
        }
    except KeyError as e:
        return jsonify({"error": f"Missing field {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    try:
        result = tenantsCollection.update_one(
            {"_id": ObjectId(tenant_id)}, {"$set": update_data}
        )
        if result.matched_count == 0:
            return jsonify({"msg": "Tenant not found"}), 404
        return jsonify({"msg": "Tenant updated successfully"}), 200
    except InvalidId:
        return jsonify({"error": "Invalid tenant ID format"}), 400
    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500


# Deactivate/Delete Tenant Account
@tenant_bp.route('/api/admin/tenants/<tenant_id>', methods=['DELETE', 'OPTIONS'])
@jwt_required()
def delete_tenant(tenant_id):
    """Update a specific tenant with a tenant_id, setting the active attribute to False.
    Args:
        tenant_id (str): tenant unique id
    """
    try:
        result = tenantsCollection.update_one(
            {"_id": ObjectId(tenant_id)}, {"$set": {"active": False}}
        )
        if result.matched_count:
            return jsonify({"msg": "Tenant deactivated"}), 204
        return jsonify({"error": "Tenant not found"}), 404
    except InvalidId:
        return jsonify({"error": "Invalid tenant ID format"}), 400
    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500


# Update Tenant Contact Information
@tenant_bp.route(
    '/api/tenants/<tenant_id>/emergencycontacts', methods=['PUT', 'OPTIONS']
)
def update_tenant_contact(tenant_id):
    """Update contact information for a specific tenant"""
    data = request.json
    try:
        update_data = {
            "emergency_contact": data['emergencyContact'],
        }
    except KeyError as e:
        return jsonify({"error": f"Missing field {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    try:
        result = tenantsCollection.update_one(
            {"_id": ObjectId(tenant_id)}, {"$set": update_data}
        )
        if result.matched_count == 0:
            return jsonify({"msg": "Tenant not found"}), 404
        return jsonify(
            {"msg": "Tenant contact information updated successfully"}
        ), 200
    except InvalidId:
        return jsonify({"error": "Invalid tenant ID format"}), 400
    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500


# Get Lease Agreements
@tenant_bp.route('/api/tenants/<tenant_id>/lease-agreements', methods=['GET', 'OPTIONS'])
def get_lease_agreements(tenant_id):
    """Get lease agreements for a specific tenant"""
    try:
        tenant = tenantsCollection.find_one(
            {"_id": ObjectId(tenant_id), "active": True}
        )
        if tenant:
            return jsonify({
                "leaseAgreementDetails": tenant['lease_agreement_details']
            }), 200
        else:
            return jsonify({"error": "Tenant not found"}), 404
    except InvalidId:
        return jsonify({"error": "Invalid tenant ID format"}), 404
    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 400
