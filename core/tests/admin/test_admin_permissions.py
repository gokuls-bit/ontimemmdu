from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from timetable.models import Semester, Section, Subject, Teacher, Room, TimeSlot, TimetableEntry


class AdminPermissionsAPITestCase(APITestCase):
    def setUp(self):
        self.super_admin = User.objects.create_superuser(username="admin", password="password123")
        self.sem5 = Semester.objects.create(number=5, academic_year="2026-27")
        self.sec_a = Section.objects.create(name="5CSEA1", semester=self.sem5, capacity=60)
        self.room357 = Room.objects.create(room_number="357", capacity=70)

    def test_admin_dashboard_api(self):
        """GET /api/v1/admin/dashboard/"""
        url = "/api/v1/admin/dashboard/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("total_students", response.data["data"])
        self.assertIn("total_teachers", response.data["data"])

    def test_admin_timetable_viewer_api(self):
        """GET /api/v1/admin/timetable/"""
        url = "/api/v1/admin/timetable/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

    def test_admin_audit_log_api(self):
        """GET /api/v1/admin/audit/"""
        url = "/api/v1/admin/audit/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
