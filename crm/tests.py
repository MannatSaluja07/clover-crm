from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import AuditLog, Contact, Deal, UserProfile


class ContactModelTests(TestCase):
    def test_full_name_combines_first_and_last(self):
        contact = Contact.objects.create(
            first_name="Aoife", last_name="Byrne", email="aoife@example.ie"
        )
        self.assertEqual(contact.full_name, "Aoife Byrne")

    def test_default_consent_status_is_pending(self):
        contact = Contact.objects.create(
            first_name="Sean", last_name="Murphy", email="sean@example.ie"
        )
        self.assertEqual(contact.consent_status, Contact.CONSENT_PENDING)


class DealModelTests(TestCase):
    def test_deal_created_with_default_stage(self):
        deal = Deal.objects.create(title="Test Deal", value=1000)
        self.assertEqual(deal.stage, Deal.STAGE_LEAD)


class AuthAndPermissionTests(TestCase):
    def setUp(self):
        self.contact = Contact.objects.create(
            first_name="Cian", last_name="Walsh", email="cian@example.ie", company="Acme"
        )

        self.admin_user = User.objects.create_user(username="admin_test", password="pass12345")
        UserProfile.objects.create(user=self.admin_user, role=UserProfile.ROLE_ADMIN)

        self.sales_user = User.objects.create_user(username="sales_test", password="pass12345")
        UserProfile.objects.create(user=self.sales_user, role=UserProfile.ROLE_SALES)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)  # redirected to login

    def test_logged_in_user_can_view_dashboard(self):
        self.client.login(username="sales_test", password="pass12345")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_sales_role_cannot_export_contact(self):
        self.client.login(username="sales_test", password="pass12345")
        response = self.client.post(
            reverse("contact_detail", args=[self.contact.pk]), {"action": "export"}
        )
        self.assertEqual(response.status_code, 403)

    def test_admin_role_can_export_contact(self):
        self.client.login(username="admin_test", password="pass12345")
        response = self.client.post(
            reverse("contact_detail", args=[self.contact.pk]), {"action": "export"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

    def test_admin_erase_anonymises_contact_and_logs_audit(self):
        self.client.login(username="admin_test", password="pass12345")
        self.client.post(
            reverse("contact_detail", args=[self.contact.pk]), {"action": "erase"}
        )
        self.contact.refresh_from_db()
        self.assertTrue(self.contact.is_anonymised)
        self.assertEqual(self.contact.consent_status, Contact.CONSENT_WITHDRAWN)
        self.assertTrue(
            AuditLog.objects.filter(contact=self.contact, action=AuditLog.ACTION_ERASE).exists()
        )
