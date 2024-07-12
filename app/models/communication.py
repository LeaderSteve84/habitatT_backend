#!/usr/bin/env python3
"""Communication models module"""
from pymongo.collection import Collection

class CommunicationModel:
    def __init__(self, collection: Collection):
        self.collection = collection

    def add_message(self, message: dict):
        result = self.collection.insert_one(message)
        return result.inserted_id

    def get_all_messages(self):
        return list(self.collection.find().sort("timestamp", 1))
