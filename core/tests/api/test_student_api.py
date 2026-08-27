import datetime
from rest_framework.test import APITestCase
from rest_framework import status
from timetable.models import (
    Semester, Section, Group, Subject, Teacher, Room, TimeSlot, TimetableEntry
)
from core.services.timetable.clock import KOLKATA_TZ


class StudentAPITestCase(APITestCase):
    def setUp(self):
        self.sem5 = Semester.objects.create(number=5, academic_year="2026-27")
        self.sec_a = Section.objects.create(name="5CSEA1", semester=self.sem5, capacity=60)
        self.grp_g1 = Group.objects.create(name="G1", section=self.sec_a)

        self.sub_os = Subject.objects.create(code="BCSE-501", name="Operating Systems", short_name="OS", semester=self.sem5)
        self.teacher1 = Teacher.objects.create(employee_id="T001", first_name="Alan", last_name="Turing", email="alan@cse.edu")
        self.room357 = Room.objects.create(room_number="357", capacity=70)

        self.slot_p2 = TimeSlot.objects.create(day="MON", period=2, start_time=datetime.time(9, 40), end_time=datetime.time(10, 40))

        TimetableEntry.objects.create(
            semester=self.sem5, section=self.sec_a, group=self.grp_g1,
            subject=self.sub_os, teacher=self.teacher1, room=self.room357,
            time_slot=self.slot_p2
        )

    def test_current_class_api(self):
        """GET /api/v1/student/current-class/"""
        url = "/api/v1/student/current-class/?semester=5&section=5CSEA1&group=G1"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("status", response.data["data"])

    def test_next_class_api(self):
        """GET /api/v1/student/next-class/"""
        url = "/api/v1/student/next-class/?semester=5&section=5CSEA1&group=G1"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("status", response.data["data"])

    def test_student_state_api(self):
        """GET /api/v1/student/state/"""
        url = "/api/v1/student/state/?semester=5&section=5CSEA1&group=G1"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("server_time", response.data["data"])
        self.assertIn("current_class", response.data["data"])
        self.assertIn("next_class", response.data["data"])
        self.assertIn("today_schedule", response.data["data"])

    def test_student_schedule_api(self):
        """GET /api/v1/student/schedule/"""
        url = "/api/v1/student/schedule/?semester=5&section=5CSEA1&group=G1&day=MON"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("schedule", response.data["data"])

    def test_student_schedule_api_orientation(self):
        """GET /api/v1/student/schedule/ with order orientation parameter."""
        url = "/api/v1/student/schedule/?semester=5&section=5CSEA1&group=G1&day=MON&order=desc"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["order"], "desc")

    def test_invalid_semester_returns_400(self):
        """GET /api/v1/student/current-class/ with invalid semester."""
        url = "/api/v1/student/current-class/?semester=99&section=5CSEA1&group=G1"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["error"]["code"], "INVALIDSEMESTER")

    def test_missing_parameters_returns_400(self):
        """GET /api/v1/student/current-class/ missing section."""
        url = "/api/v1/student/current-class/?semester=5"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
