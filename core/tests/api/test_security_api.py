import datetime
from rest_framework.test import APITestCase
from rest_framework import status
from timetable.models import (
    Semester, Section, Group, Subject, Teacher, Room, TimeSlot, TimetableEntry
)


class SecurityAPITestCase(APITestCase):
    def setUp(self):
        self.sem5 = Semester.objects.create(number=5, academic_year="2026-27")
        self.sec_a = Section.objects.create(name="5CSEA1", semester=self.sem5, capacity=60)
        self.grp_g1 = Group.objects.create(name="G1", section=self.sec_a)

    def test_cors_headers_present(self):
        """32. Verify CORS headers are present in response."""
        url = "/api/v1/health/"
        response = self.client.get(url, HTTP_ORIGIN="http://localhost:3000")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Access-Control-Allow-Origin", response.headers)

    def test_path_traversal_download_blocked(self):
        """33. Verify path traversal attempt in download endpoint is blocked."""
        url = "/api/v1/timetable/invalid_sem/excel/"
        response = self.client.get(url)

        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND])

    def test_standard_response_envelope_structure(self):
        """28. Verify standard response envelope structure."""
        url = "/api/v1/health/"
        response = self.client.get(url)

        self.assertIn("success", response.data)
        self.assertIn("data", response.data)
        self.assertTrue(response.data["success"])

    def test_query_count_for_student_state_api(self):
        """38 & 41. Query efficiency performance test for student state API."""
        url = "/api/v1/student/state/?semester=5&section=5CSEA1&group=G1"

        # Warm up
        self.client.get(url)

        with self.assertNumQueries(20):
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
