#!/usr/bin/env python3
"""Model for properties"""


from bson.objectid import ObjectId
from datetime import datetime


class Property:
    """Class representing a property instance"""
    def __init__(
        self, address, property_type, unit_availability,
        rental_fees, property_id=None
    ):
        """
        Initializer/object constructor.
        Args:
            address (str): Address of the property
            property_type (str): Type of the property
            unit_availability  (bool): Availability of units in the property
            rental_fees  (float): Rental fees for the property
        """
        self.property_id = property_id if property_id else ObjectId()
        self.date_created = datetime.now()
        self.address = address
        self.property_type = property_type
        self.unit_availability = unit_availability
        self.rental_fees = rental_fees

    def to_dict(self):
        """Returns the dictionary of all the property attributes"""
        return {
            "_id": self.property_id,
            "date_created": self.address,
            "address": self.address,
            "type": self.property_type,
            "unit_availability": self.unit_availability,
            "rental_fees": self.rental_fees
        }
