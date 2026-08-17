from django.contrib.auth.models import Permission, User
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Complaint


class VigilanceManagementApiTests(APITestCase):
    def setUp(self):
        self.complaint = Complaint.objects.create(description="Test complaint")
        self.user = User.objects.create_user("ordinary", password="test-password")
        self.officer = User.objects.create_user("officer", password="test-password")
        self.officer.user_permissions.add(
            Permission.objects.get(codename="manage_complaints")
        )
        self.list_url = "/api/v1/vigilance/admin/complaints/"
        self.detail_url = f"{self.list_url}{self.complaint.pk}/"

    def test_non_officer_cannot_read_cases(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_officer_can_only_update_status(self):
        self.client.force_authenticate(self.officer)

        self.assertEqual(self.client.post(self.list_url, {}).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.delete(self.detail_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(
            self.detail_url, {"description": "Altered"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.complaint.refresh_from_db()
        self.assertEqual(self.complaint.description, "Test complaint")

        response = self.client.patch(
            self.detail_url, {"status": "resolved"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.complaint.refresh_from_db()
        self.assertEqual(self.complaint.status, "resolved")
