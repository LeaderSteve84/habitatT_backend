#!/usr/bin/env python3
"""Model for log requests"""
from bson.objectid import ObjectId
from datetime import datetime


class LogRequest:
    """Class for the log request instance"""
    def __init__(
        self, request_type="", urgency_level="", property_address="",
        description="", submitted_date=None, status="pending",
        logged_by="", log_request_id=None, archive=False
    ):
        """Initializer/object constructor.
        Args:
            request_type  (str): Type of the request
            urgency_level  (str): Urgency level of the request
            property_address (str): Address of the property
            related to the request
            description  (str): Description of the request
            submitted_date  (datetime): Date the request was submitted
            status  (str): Status of the request
            archive (bool): Archive status of the request
        """
        self.log_request_id = log_request_id if log_request_id else ObjectId()
        self.submitted_date = submitted_date if submitted_date \
            else datetime.now()
        self.request_type = request_type
        self.urgency_level = urgency_level
        self.property_address = property_address
        self.description = description
        self.logged_by = logged_by
        self.status = status
        self.archive = archive

    def to_dict(self):
        """Returns the dictionary of all the LogRequest attribute
        """
        return {
            "_id": self.log_request_id,
            "submitted_date": self.submitted_date,
            "request_type": self.request_type,
            "urgency_level": self.urgency_level,
            "property_address": self.property_address,
            "description": self.description,
            "logged_by": self.logged_by,
            "status": self.status,
            "archive": self.archive
        }
