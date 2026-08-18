from django.test import TestCase, Client
from django.urls import reverse


class DownloadsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_valid_json_download_endpoint(self):
        """30. JSON export/download endpoint test."""
        response = self.client.get('/timetable/download/3rd/json/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        self.assertEqual(data['semester'], '3rd Semester')
        self.assertIn('dataset', data)

    def test_invalid_semester_download_attempt(self):
        """33. Attempt to download an unregistered file/semester."""
        response = self.client.get('/timetable/download/99th/json/')
        self.assertEqual(response.status_code, 400)

    def test_invalid_format_download_attempt(self):
        """Invalid format rejection."""
        response = self.client.get('/timetable/download/3rd/exe/')
        self.assertEqual(response.status_code, 400)
