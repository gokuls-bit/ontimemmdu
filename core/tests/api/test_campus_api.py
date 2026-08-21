from rest_framework.test import APITestCase
from rest_framework import status
from timetable.models import Semester, Section, Group


class CampusAPITestCase(APITestCase):
    def setUp(self):
        self.sem5 = Semester.objects.create(number=5, academic_year="2026-27")
        self.sec_a = Section.objects.create(name="5CSEA1", semester=self.sem5, capacity=60)
        self.grp_g1 = Group.objects.create(name="G1", section=self.sec_a)

    def test_campus_occupancy_api(self):
        """GET /api/v1/campus/occupancy/"""
        url = "/api/v1/campus/occupancy/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("total_rooms", response.data["data"])
        self.assertIn("utilization_percentage", response.data["data"])

    def test_metadata_semesters_api(self):
        """GET /api/v1/metadata/semesters/"""
        url = "/api/v1/metadata/semesters/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 1)

    def test_metadata_sections_api(self):
        """GET /api/v1/metadata/sections/"""
        url = "/api/v1/metadata/sections/?semester=5"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 1)

    def test_health_check_api(self):
        """GET /api/v1/health/"""
        url = "/api/v1/health/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["status"], "healthy")
