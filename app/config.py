#!/usr/bin/env python3
"""configurations module"""
import os
from dotenv import load_dotenv
import ast
from flask import has_request_context, request
import logging
# Load environmental variables from .env file
load_dotenv()


class Config:
    FLASK_RUN = os.environ.get('FLASK_APP')
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MONGO_URI = os.environ.get('MONGO_URI')
    MONGO_DB_NAME = os.environ.get('MONGO_DB_NAME')
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_TOKEN_LOCATION = ast.literal_eval(os.environ.get('JWT_TOKEN_LOCATION'))
    JWT_COOKIE_SECURE = os.environ.get('JWT_COOKIE_SECURE')
    JWT_COOKIE_CSRF_PROTECT = False  # Add this line to disable CSRF protection


class TestingConfig(Config):
    TESTING = True
    MONGO_DB_NAME = os.environ.get('TEST_MONGO_DB_NAME')
    JWT_COOKIE_SECURE = False  # insecure for testing purpose


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None

        return super().format(record)
