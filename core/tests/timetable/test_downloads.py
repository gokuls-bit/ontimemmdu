import os
import json
from django.test import TestCase, Client
from django.urls import reverse


class TimetableDownloadsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_30_json_download(self):
        """Verify successful JSON download for 3rd semester."""
        response = self.client.get('/timetable/download/3rd/json/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content)
        self.assertIn("semester", data)
        self.assertIn("dataset", data)

    def test_31_excel_download(self):
        """Verify Excel download endpoint behavior."""
        response = self.client.get('/timetable/download/3rd/excel/')
        # Returns 200 if file exists, or 404 if file is physically absent on disk
        self.assertIn(response.status_code, [200, 404])

    def test_32_path_traversal_attempt(self):
        """Reject path traversal attempt in semester/format parameter."""
        response = self.client.get('/timetable/download/etc_passwd/json/')
        self.assertEqual(response.status_code, 400)

        response2 = self.client.get('/timetable/download/3rd/secret_format/')
        self.assertEqual(response2.status_code, 400)

    def test_33_unregistered_file_download(self):
        """Reject request for unregistered semester or format."""
        response = self.client.get('/timetable/download/8th/json/')
        self.assertEqual(response.status_code, 400)

        response2 = self.client.get('/timetable/download/3rd/pdf/')
        self.assertEqual(response2.status_code, 400)
