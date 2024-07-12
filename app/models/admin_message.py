#!/usr/bin/env python3
"""model for admin messages"""
from bson.objectid import ObjectId
from datetime import datetime


class AdminMessage:
    """Class of the admin message instance"""
    def __init__(self, message, title, message_id=None):
        """Initializer/object constructor.
        Args:
            message (str): The message content
            title  (str): The title of the message
            date  (str): The date of the message
        """

        self.message_id = message_id if message_id else ObjectId()
        self.date_created = datetime.now()
        self.message = message
        self.title = title

    def to_dict(self):
        """returns the dictionary of all
        the AdminMessage attricutes
        """
        return {
            "_id": self.message_id,
            "date_created": self.date_created,
            "message": self.message,
            "title": self.title
        }
