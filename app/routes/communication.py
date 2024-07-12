#!/usr/bin/env python3
"""Communication routes module"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from bson import ObjectId
from app import socketio
from app.models.communication import CommunicationModel
from flask_socketio import emit

communication_bp = Blueprint('communication_bp', __name__)

tenantsCollection = current_app.tenantsCollection
adminsCollection = current_app.adminsCollection
messagesCollection = current_app.messagesCollection

communication_model = CommunicationModel(messagesCollection)

def convert_objectid(obj):
    """Recursively convert ObjectIds to strings in a given object."""
    if isinstance(obj, list):
        return [convert_objectid(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_objectid(value) for key, value in obj.items()}
    elif isinstance(obj, ObjectId):
        return str(obj)
    else:
        return obj

@communication_bp.route('/api/messages', methods=['GET'])
@jwt_required()
def get_messages():
    messages = list(messagesCollection.find())
    messages = convert_objectid(messages)  # Convert ObjectId to string
    return jsonify(messages), 200

from datetime import datetime

@communication_bp.route('/api/send_message', methods=['POST'])
@jwt_required()
def send_message():
    try:
        identity = get_jwt_identity()
        print(f"Identity: {identity}")  # Debug print

        if 'email' not in identity or 'role' not in identity:
            print("Invalid token data")
            return jsonify({"msg": "Invalid token data"}), 400

        user_collection = adminsCollection if identity['role'] == 'admin' else tenantsCollection
        user = user_collection.find_one({"contact_details.email": identity['email']})
        if not user:
            print("User not found")
            return jsonify({"msg": "User not found"}), 404

        message = request.json.get('message')
        if not message:
            print("Invalid data")
            return jsonify({"msg": "Invalid data"}), 400

        # Format the timestamp to a readable format
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        full_name = f"{user['name']['fname']} {user['name']['lname']}"
        msg = {
            'name': full_name,
            'message': message,
            'timestamp': timestamp
        }

        # Add message to the collection and convert the ObjectId to string
        inserted_id = communication_model.add_message(msg)
        msg['_id'] = str(inserted_id)  # Ensure the _id is a string

        # Emit the message to the 'receive_message' event without 'broadcast=True'
        socketio.emit('receive_message', msg)

        return jsonify(msg), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"msg": "An error occurred"}), 500
