#!/usr/bin/env python3
"""All routes for admin message CRUD operations"""
from flask import Blueprint, request, jsonify, current_app
from bson.objectid import ObjectId
from app.models.admin_message import AdminMessage
from pymongo.errors import PyMongoError
from bson.errors import InvalidId


admin_message_bp = Blueprint('admin_message', __name__)

adminMessagesCollection = current_app.adminMessagesCollection

# Create Admin Message
@admin_message_bp.route('/api/admin/messages', methods=['POST'])
def create_message():
    """Create an admin message.
       POST message to MongoDB database.
       Return: "msg": "Message created successfully" and success status
    """
    data = request.json
    try:
        message = AdminMessage(
            message=data['message'],
            title=data['title'],
        )
    except KeyError as e:
        return jsonify({"error": f"Missing field {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    try:
        insert_result = adminMessagesCollection.insert_one(message.to_dict())
    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500
    message_id = insert_result.inserted_id
    return jsonify(
        {"msg": "Message created successfully", "messageId": str(message_id)}
    ), 201


# Get all Admin Messages
@admin_message_bp.route('/api/admin/messages', methods=['GET'])
def get_all_messages():
    """Find all messages from MongoDB and return list of all the messages"""
    try:
        messages = adminMessagesCollection.find()
        messages_list = [{
            "messageId": str(message['_id']),
            "dateCreated": message['date_created'],
            "message": message['message'],
            "title": message['title']
        } for message in messages]
        return jsonify(messages_list), 200
    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500


# Update Specific Admin Message
@admin_message_bp.route('/api/admin/messages/<message_id>', methods=['PUT'])
def update_message(message_id):
    """Update a specific admin message with a message_id.
    Args:
        message_id  (str): message unique id
    """
    data = request.json
    try:
        update_data = {
            "message": data['message'],
            "title": data['title']
        }
    except KeyError as e:
        return jsonify({"error": f"Missing field {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    try:
        result = adminMessagesCollection.update_one(
            {"_id": ObjectId(message_id)}, {"$set": update_data}
        )
        if result.matched_count == 0:
            return jsonify({"msg": "Message not found"}), 404
        return jsonify({"msg": "Message updated successfully"}), 200
    except InvalidId:
        return jsonify({"error": "Invalid tenant ID format"}), 404
    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500


# Delete Admin Message
@admin_message_bp.route('/api/admin/messages/<message_id>', methods=['DELETE'])
def delete_message(message_id):
    """Delete a specific admin message with a message_id
    Args:
    message_id  (str): message unique id
    """
    try:
        result = adminMessagesCollection.delete_one(
            {"_id": ObjectId(message_id)}
        )
        if result.deleted_count == 0:
            return jsonify({"error": "Message not found"}), 404
        return jsonify({"msg": "Message deleted successfully"}), 204
    except InvalidId:
        return jsonify({"error": "Invalid tenant ID format"}), 404
    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500
