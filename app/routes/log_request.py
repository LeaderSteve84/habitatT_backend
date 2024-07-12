#!/usr/bin/env python3
"""All routes for log request CRUD operations"""
from flask import Blueprint, request, jsonify, current_app
from bson.objectid import ObjectId
from app.models.log_request import LogRequest
from pymongo.errors import PyMongoError
from bson.errors import InvalidId


log_request_bp = Blueprint('log_request', __name__)
logRequestsCollection = current_app.logRequestsCollection

# Create Log Request
@log_request_bp.route('/api/admin/log-requests', methods=['POST'])
def create_log_request():
    """Create log request as instance of LogRequest.
       Post log request to MongoDB database.
       Return: "msg": "Log request created successfully"
       and success status
    """
    data = request.json
    try:
        log_request_instance = LogRequest(
            request_type=data.get('requestType', ''),
            urgency_level=data.get('urgencyLevel', ''),
            property_address=data.get('propertyAddress', ''),
            description=data.get('description', ''),
            logged_by=data.get('loggedBy', '')
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    try:
        insert_result = logRequestsCollection.insert_one(
            log_request_instance.to_dict()
        )
    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500

    log_request_id = insert_result.inserted_id
    return jsonify(
        {
            "msg": "Log request created successfully",
            "requestId": str(log_request_id)
        }
    ), 201


# Get All Open Log Requests
@log_request_bp.route('/api/admin/log-requests', methods=['GET'])
def get_all_log_requests():
    """Find all open log requests from MongoDB and
    return list of all the open log requests
    """

    try:
        log_requests = logRequestsCollection.find(
            {"status": {"$ne": "resolved"}, "archive": False}
        )
        log_requests_list = [{
            "requestedId": str(log_request['_id']),
            "loggedBy": log_request['logged_by'],
            "submittedDate": log_request['submitted_date'],
            "requestType": log_request['request_type'],
            "urgencyLevel": log_request['urgency_level'],
            "propertyAddress": log_request['property_address'],
            "description": log_request['description'],
            "status": log_request['status']
        } for log_request in log_requests]
        return jsonify(log_requests_list), 200
    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500


# Get Specific Log Request Details
@log_request_bp.route('/api/admin/log-requests/<request_id>', methods=['GET'])
def get_log_request(request_id):
    try:
        log_request = logRequestsCollection.find_one(
            {"_id": ObjectId(request_id)}
        )
        if log_request:
            return jsonify({
                "requestId": str(log_request['_id']),
                "loggedBy": log_request['logged_by'],
                "submittedDate": log_request['submitted_date'],
                "requestType": log_request['request_type'],
                "urgencyLevel": log_request['urgency_level'],
                "propertyAddress": log_request['property_address'],
                "description": log_request['description'],
                "status": log_request['status']
            }), 200
        else:
            return jsonify({"error": "Log request not found"}), 404
    except InvalidId:
        return jsonify({"error": "Invalid tenant ID format"}), 404
    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Update Log Request
@log_request_bp.route('/api/admin/log-requests/<request_id>', methods=['PUT'])
def update_log_request(request_id):
    """Update a specific log request with a request_id.
    Args:
        request_id  (str): Log request unique id
    """
    data = request.json
    try:
        update_data = {
            "request_type": data.get('requestType', ''),
            "logged_by": data.get('loggedBy', ''),
            "urgency_level": data.get('urgencyLevel', ''),
            "property_address": data.get('propertyAddress', ''),
            "description": data.get('description', ''),
            "status": data.get('status', 'pending')
        }
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    try:
        result = logRequestsCollection.update_one(
            {"_id": ObjectId(request_id)}, {"$set": update_data}
        )
        if result.matched_count == 0:
            return jsonify({"msg": "Log request not found"}), 404
        return jsonify({"msg": "Log request updated successfully"}), 200
    except InvalidId:
        return jsonify({"error": "Invalid tenant ID format"}), 404
    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500


# Update Log Request Status
@log_request_bp.route(
    '/api/admin/log-requests/<request_id>/status', methods=['PUT']
)
def update_log_request_status(request_id):
    """Update the status of a specific log request with a request_id.
    Args:
        request_id (str): Log request unigue id
    """
    data = request.json
    try:
        update_data = {
            "status": data.get('status', 'pendimg')
        }
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    try:
        result = logRequestsCollection.update_one(
            {"_id": ObjectId(request_id)}, {"$set": update_data}
        )
        if result.matched_count == 0:
            return jsonify({"msg": "Log request not found"}), 404
        return jsonify({"msg": "Log request status updated successfully"}), 200
    except InvalidId:
        return jsonify({"error": "Invalid tenant ID format"}), 404
    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500


# Archive Log Request
@log_request_bp.route(
    '/api/admin/log-requests/<request_id>/archive', methods=['PUT']
)
def archive_log_request(request_id):
    """Archive a specific log request with a request_id.
    Args:
        request_id (str): Log request unique id
    """
    data = request.json
    try:
        update_data = {
            "archive": data.get('archive', False)
        }
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    try:
        result = logRequestsCollection.update_one(
            {"_id": ObjectId(request_id)}, {"$set": update_data}
        )
        if result.matched_count == 0:
            return jsonify({"msg": "Log request not found"}), 404
        return jsonify({"msg": "Log request archived successfully"}), 200
    except InvalidId:
        return jsonify({"error": "Invalid tenant ID format"}), 404
    except PymongoError as e:
        return jsonify({"error": str(e)}), 500


# close Log Request
@log_request_bp.route(
    '/api/admin/log-requests/<request_id>/close', methods=['PUT']
)
def close_log_request(request_id):
    """Close a specific log request with a request_id.
    Args:
        request_id (str): Log request unique id
    """
    data = request.json
    try:
        update_data = {
            "status": data.get('status', 'resolved')
        }
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    try:
        result = logRequestsCollection.update_one(
            {"_id": ObjectId(request_id)}, {"$set": update_data}
        )
        if result.matched_count == 0:
            return jsonify({"msg": "Log request not found"}), 404
        return jsonify({"msg": "Log request closed successfully"}), 200
    except InvalidId:
        return jsonify({"error": "Invalid tenant ID format"}), 404
    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500
