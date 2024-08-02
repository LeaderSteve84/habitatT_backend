#!/usr/bin/env python3
"""All routes for property CRUD operations"""
from flask import Blueprint, request, jsonify, current_app
from bson.objectid import ObjectId
from app.models.property import Property
from pymongo.errors import PyMongoError
from bson.errors import InvalidId


property_bp = Blueprint('property', __name__)

propertiesCollection = current_app.propertiesCollection

# Create Property
@property_bp.route('/api/admin/properties', methods=['POST', 'OPTIONS'])
def create_property():
    """Create a new property instance and store it in the database.
       Return: "msg": "Property created successfully"
       and success status
    """
    data = request.json
    try:
        property = Property(
            address=data['address'],
            property_type=data['type'],
            unit_availability=data['unitAvailability'],
            rental_fees=data['rentalFees']
        )
    except KeyError as e:
        return jsonify({"error": f"Missing field {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    try:
        insert_result = propertiesCollection.insert_one(property.to_dict())
    except Exception as e:
        return jsonify({"eror": str(e)}), 500

    property_id = insert_result.inserted_id
    return jsonify(
        {"msg": "prop. created successfully", "prop_Id": str(property_id)}
    ), 201


# Get All Properties
@property_bp.route('/api/admin/properties', methods=['GET', 'OPTIONS'])
def get_all_properties():
    """Retrieve all properties from the database.
    Return: List of properties
    """

    try:
        properties = propertiesCollection.find()
        properties_list = [{
            "propertyId": str(property['_id']),
            "dateCreated": property['date_created'],
            "address": property['address'],
            "type": property['type'],
            "unitAvailability": property['unit_availability'],
            "rentalFees": property['rental_fees']
        } for property in properties]
        return jsonify(properties_list), 200
    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500


# Get Specific Property Details
@property_bp.route('/api/admin/properties/<property_id>', methods=['GET', 'OPTIONS'])
def get_specific_property(property_id):
    """Retrieve details of a specific property by ID.
    """
    try:
        property = propertiesCollection.find_one(
            {"_id": ObjectId(property_id)}
        )
        if property:
            return jsonify({
                "propertyId": str(property['_id']),
                "dateCreated": property['date_created'],
                "address": property['address'],
                "type": property['type'],
                "unitAvailability": property['unit_availability'],
                "rentalFees": property['rental_fees']
            }), 200
        else:
            return jsonify({"error": "Property not found"}), 404
    except InvalidId:
        return jsonify({"error": "Invalid tenant ID format"}), 404
    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Update Property Details
@property_bp.route('/api/admin/properties/<property_id>', methods=['PUT', 'OPTIONS'])
def update_property(property_id):
    """Update a specific property by ID."""
    data = request.json
    try:
        update_data = {
            "address": data['address'],
            "type": data['type'],
            "unit_availability": data['unitAvailability'],
            "rental_fees": data['rentalFees']
        }
    except KeyError as e:
        return jsonify({"error": f"Missing field {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    try:
        result = propertiesCollection.update_one(
            {"_id": ObjectId(property_id)}, {"$set": update_data}
        )
        if result.matched_count == 0:
            return jsonify({"msg": "Property not found"}), 404
        return jsonify({"msg": "Property updated successfully"}), 200
    except InvalidId:
        return jsonify({"error": "Invalid Property ID format"}), 404
    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500


# Delete Property
@property_bp.route('/api/admin/properties/<property_id>', methods=['DELETE', 'OPTIONS'])
def delete_property(property_id):
    """Dlete a specific property by ID."""
    try:
        result = propertiesCollection.delete_one(
            {"_id": ObjectId(property_id)}
        )
        if result.deleted_count:
            return jsonify({"msg": "Property deleted successfully"}), 204
        return jsonify({"error": "Property not found"}), 404
    except InvalidId:
        return jsonify({"error": "Invalid tenant ID format"}), 404
    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500
