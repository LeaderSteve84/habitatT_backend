#!/usr/bin/env python3
"""
test_tenant_creation.py

This module contains unit tests for the
tenant creation endpoint in the Flask application.
It tests the POST /api/admin/tenants endpoint to ensure
that a tenant account can be created successfullyy.

Classes:
    TenantCreationTestCase: Unit test Case for testing tenant creation.

Functions:
    setUp: Set up the test environment before each test.
    tearDown: Clean up the test environment after each test.
    test_create_tenant: Test case for creating a tenant account.
"""

import unittest
from flask import current_app
from app import create_app
from flask_jwt_extended import create_access_token
from io import BytesIO
import json


class TenantCreationTestCase(unittest.TestCase):
    """
    Unit test case for testing tenant creation.

    Methods:
        setUp: Set up the test environment before each test.
        tearDown: clean up the test environment after each test.
        test_create_tenant: Test case for creating a tenant account.
    """

    ENDPOINT = '/api/admin/tenants'

    def setUp(self):
        """
        Set up the test environment before each test.

        This method initializes the Flask test client and
        sets up the application context.
        """
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Generate a test JWT token
        with self.app.test_request_context():
            self.token = create_access_token(identity='test_user')

        self.headers = {
            'Authorization': 'Bearer ' + self.token,
            'Content-Type': 'application/json',
        }

        self.tenantsCollection = current_app.tenantsCollection

    def tearDown(self):
        """
        Clean up the test environment after each test.

        This method pops the application context.
        """
        self.tenantsCollection.delete_many(
            {"contact_details.email": "mike.doe@example.com"}
        )
        self.app_context.pop()

def test_create_tenant(self):
        """
        Test case for creating a tenant account.

        This method sends a POST request to te /api/admin/tenants
        endpoint with tenant data and asserts that the tenant
        account is created successfully.
        """
        tenant_data = {
            "name": {"fname": "Mike", "lname": "Doe"},
            "password": "password123",
            "DoB": "1990-01-01",
            "sex": "M",
            "contactDetails": {
                "email": "mike.doe@example.com",
                "phone": "1234567890",
                "address": "123 Main St"
            },
            "emergencyContact": {
                "name": "Jane Doe", "phone": "0987654321",
                "address": "457 Sahdai St"
            },
            "tenancyInfo": {
                "fees": 1000, "paid": 500, "datePaid": "2022-01-15",
                "start": "2022-01-01", "expires": "2022-12-31", "arrears": "0"
            },
            "leaseAgreementDetails": "http://example.com/lease.pdf"
        }

        response = self.client.post(
            self.ENDPOINT,
            headers=self.headers,
            content_type='application/json',
            data=json.dumps(tenant_data)
        )

        self.assertEqual(response.status_code, 201)
        response_data = response.get_json()
        self.assertIn('tenantId', response_data)
        self.assertEqual(
            response_data['msg'], 'Tenant created successfully'
        )

        # Verify that the tenant was inserted into the database
        tenant = self.tenantsCollection.find_one(
            {"contact_details.email": "mike.doe@example.com"}
        )
        self.assertIsNotNone(tenant)
        self.assertEqual(tenant['name']['fname'], 'Mike')
        self.assertEqual(tenant['name']['lname'], 'Doe')

def test_create_tenant_missing_fields(self):
        """
        Test case for creating a tenant account with missing required fields..
        """
        tenant_data = {
            "name": {"fname": "Mike"},
            "password": "password123",
            "DoB": "1990-01-01",
            "sex": "M",
            "contactDetails": {
                "email": "mike.kush@example.com",
                "phone": "1234567890",
                "address": "145 Oramo St"
            },
            "emergencyContact": {
                "name": "Jane Kush", "phone": "0987654321",
                "address": "457 Sahdai St"
            },
            "tenancyInfo": {
                "fees": 1000, "paid": 500, "datePaid": "2022-01-15",
                "start": "2022-01-01", "expires": "2022-12-31", "arrears": "0"
            },
            "leaseAgreementDetails": "http://example.com/lease.pdf"
        }

        response = self.client.post(
            self.ENDPOINT,
            headers=self.headers,
            content_type='application/json',
            data=json.dumps(tenant_data)
        )

        self.assertEqual(response.status_code, 400)
        response_data = response.get_json()
        self.assertEqual(
            response_data['msg'], 'Missing required fields'
        )

def test_create_tenant_invalid_email(self):
        """
        Test case for creating a tenant with an invalid email format.
        """
        tenant_data = {
            "name": {"fname": "Mike", "lname": "Doe"},
            "password": "password123",
            "DoB": "1990-01-01",
            "sex": "F",
            "contactDetails": {
                "email": "jane.doe",
                "phone": "1234567890",
                "address": "145 Oramo St"
            },
            "emergencyContact": {
                "name": "Jane Kush", "phone": "0987654321",
                "address": "457 Sahdai St"
            },
            "tenancyInfo": {
                "fees": 1000, "paid": 500, "datePaid": "2022-01-15",
                "start": "2022-01-01", "expires": "2022-12-31", "arrears": "0"
            },
            "leaseAgreementDetails": "http://example.com/lease.pdf"
        }

        response = self.client.post(
            self.ENDPOINT,
            headers=self.headers,
            content_type='application/json',
            data=json.dumps(tenant_data)
        )

        self.assertEqual(response.status_code, 400)
        response_data = response.get_json()
        self.assertEqual(
            response_data['msg'], 'Invalid email format'
        )


if __name__ == '__main__':
    unittest.main()
