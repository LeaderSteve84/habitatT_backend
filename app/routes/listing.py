#!/usr/bin/env python3
"""All routes for property listing CRUD operations"""
from flask import Blueprint, request, jsonify, current_app
from bson.objectid import ObjectId
from app.models.listing import Listing
from pymongo.errors import PyMongoError
from bson.errors import InvalidId
from flask_jwt_extended import jwt_required, get_jwt_identity

listing_bp = Blueprint('listing', __name__)

listingCollection = current_app.listingCollection


# Create listing
@listing_bp.route('/api/admin/properties-listing', methods=['POST', 'OPTIONS'])
def create_property_listing():
    """Create a new property listing instance and store it in the database.
       Return: "msg": "listing created successfully"
       and success status
    """
    data = request.json
    try:
        listing = Listing(
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
        insert_result = listingCollection.insert_one(listing.to_dict())
    except Exception as e:
        return jsonify({"eror": str(e)}), 500

    listing_id = insert_result.inserted_id
    return jsonify(
        {
            "msg": "list. created successfully", "listed_prop_Id": str(
                listing_id
            )
        }
    ), 201


# Get All Listed Properties
@listing_bp.route('/api/admin/properties-listing', methods=['GET', 'OPTIONS'])
def get_all_listed_properties():
    """Retrieve all properties listed from the database.
    Return: List of listed properties
    """

    try:
        listed_properties = listingCollection.find()
        listed_properties_list = [{
            "propertyId": str(listed_property['_id']),
            "dateCreated": listed_property['date_created'],
            "address": listed_property['address'],
            "type": listed_property['type'],
            "unitAvailability": listed_property['unit_availability'],
            "rentalFees": listed_property['rental_fees']
        } for listed_property in listed_properties]
        return jsonify(listed_properties_list), 200
    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500


# Get Specific listed Property Details
@listing_bp.route(
    '/api/admin/properties-listing/<listing_id>', methods=['GET', 'OPTIONS']
)
def get_listed_property(listing_id):
    """Retrieve details of a specific listed property by ID.
    """
    try:
        listed_property = listingCollection.find_one(
            {"_id": ObjectId(listing_id)}
        )
        if listed_property:
            return jsonify({
                "propertyId": str(listed_property['_id']),
                "dateCreated": listed_property['date_created'],
                "address": listed_property['address'],
                "type": listed_property['type'],
                "unitAvailability": listed_property['unit_availability'],
                "rentalFees": listed_property['rental_fees']
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
@listing_bp.route(
    '/api/admin/properties-listing/<listing_id>', methods=['PUT', 'OPTIONS']
)
def update_property(listing_id):
    """Update a specific listed property by ID."""
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
        result = listingCollection.update_one(
            {"_id": ObjectId(listing_id)}, {"$set": update_data}
        )
        if result.matched_count == 0:
            return jsonify({"msg": "Listed property not found"}), 404
        return jsonify({"msg": "Listed property updated successfully"}), 200
    except InvalidId:
        return jsonify({"error": "Invalid Listed Property ID format"}), 404
    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500


# Delete Listed Property
@listing_bp.route(
    '/api/admin/properties-listing/<listing_id>', methods=['DELETE', 'OPTIONS']
)
def delete_listed_property(listing_id):
    """Delete a specific listed property by ID."""
    try:
        result = listingCollection.delete_one({"_id": ObjectId(listing_id)})
        if result.deleted_count:
            return jsonify(
                {"msg": "listed Property deleted successfully"}
            ), 204
        return jsonify({"error": "listed property not found"}), 404
    except InvalidId:
        return jsonify({"error": "Invalid tenant ID format"}), 404
    except PyMongoError as e:
        return jsonify({"error": str(e)}), 500
