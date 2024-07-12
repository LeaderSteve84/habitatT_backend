#!/usr/bin/env python3
"""model for admins"""
from bson.objectid import ObjectId
from datetime import datetime


class Admin:
    """class of the admin instance"""
    def __init__(
        self, name, password, dob, sex, contact_details, emergency_contact, role, admin_id=None,
        active=True
    ):
        """Initializer/object constructor.
        Args:
            name (dict): dictionary containing the fname and lname
            dob  (time): date of birth
            sex  (str):  sex
            contact_details (dict): dict of phone, email, and address.
            emergency_contact (dict): dict name, phone, address
            active  (bool): Status of Tenancy. True by default
        """
        self.admin_id = admin_id if admin_id else ObjectId()
        self.date_created = datetime.now()
        self.name = name
        self.password = password  # hashed password
        self.dob = dob
        self.sex = sex
        self.contact_details = contact_details
        self.emergency_contact = emergency_contact
        self.role = role
        self.active = active

    def to_dict(self):
        """returns the dictionary of all the admin attributes"""
        return {
            "_id": self.admin_id,
            "date_created": self.date_created,
            "name": self.name,
            "password": self.password,
            "dob": self.dob,
            "sex": self.sex,
            "contact_details": self.contact_details,
            "emergency_contact": self.emergency_contact,
            "active": self.active,
            "role": self.role
        }
