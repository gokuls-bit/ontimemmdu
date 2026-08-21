import datetime
from rest_framework.test import APITestCase
from rest_framework import status
from timetable.models import Semester, Section, Group, Subject, Teacher, Room, TimeSlot, TimetableEntry


class TeacherAPITestCase(APITestCase):
    def setUp(self):
        self.sem5 = Semester.objects.create(number=5, academic_year="2026-27")
        self.sec_a = Section.objects.create(name="5CSEA1", semester=self.sem5, capacity=60)
        self.room357 = Room.objects.create(room_number="357", capacity=70)
        self.sub_os = Subject.objects.create(code="BCSE-501", name="Operating Systems", short_name="OS", semester=self.sem5)

        self.teacher1 = Teacher.objects.create(employee_id="T001", first_name="Alan", last_name="Turing", email="alan@cse.edu")
        self.slot_p2 = TimeSlot.objects.create(day="MON", period=2, start_time=datetime.time(9, 40), end_time=datetime.time(10, 40))

        TimetableEntry.objects.create(
            semester=self.sem5, section=self.sec_a,
            subject=self.sub_os, teacher=self.teacher1, room=self.room357,
            time_slot=self.slot_p2
        )

    def test_teacher_search_api(self):
        """GET /api/v1/teachers/search/?q=Turing"""
        url = "/api/v1/teachers/search/?q=Turing"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 1)

    def test_teacher_location_api(self):
        """GET /api/v1/teachers/T001/location/"""
        url = "/api/v1/teachers/T001/location/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["teacher"], "Alan Turing")

    def test_all_teacher_status_api(self):
        """GET /api/v1/teachers/status/"""
        url = "/api/v1/teachers/status/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

    def test_unknown_teacher_returns_404(self):
        """GET /api/v1/teachers/INVALID_TEACHER/location/"""
        url = "/api/v1/teachers/INVALID_TEACHER/location/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["error"]["code"], "TEACHERNOTFOUND")
