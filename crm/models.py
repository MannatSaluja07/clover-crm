from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    """
    Extends Django's built-in User with a CRM role.

    Kept as a separate model (rather than a custom User) so auth stays on
    Django's well-tested built-in system — only the role concept is ours.
    """

    ROLE_ADMIN = "admin"
    ROLE_SALES = "sales"
    ROLE_MANAGER = "manager"
    ROLE_CHOICES = [
        (ROLE_ADMIN, "Admin"),
        (ROLE_SALES, "Sales"),
        (ROLE_MANAGER, "Manager"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_SALES)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN


class Contact(models.Model):
    """
    A person the business has a relationship with.

    consent_status and is_anonymised exist specifically to support GDPR /
    Irish Data Protection Act obligations: consent tracking and the right
    to erasure.
    """

    CONSENT_GRANTED = "granted"
    CONSENT_PENDING = "pending"
    CONSENT_WITHDRAWN = "withdrawn"
    CONSENT_CHOICES = [
        (CONSENT_GRANTED, "Granted"),
        (CONSENT_PENDING, "Pending"),
        (CONSENT_WITHDRAWN, "Withdrawn"),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30, blank=True)
    company = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=100, blank=True)
    consent_status = models.CharField(
        max_length=20, choices=CONSENT_CHOICES, default=CONSENT_PENDING
    )
    is_anonymised = models.BooleanField(
        default=False,
        help_text="True once this contact's PII has been erased on request.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Deal(models.Model):
    STAGE_LEAD = "lead"
    STAGE_PROPOSAL = "proposal"
    STAGE_WON = "won"
    STAGE_LOST = "lost"
    STAGE_CHOICES = [
        (STAGE_LEAD, "Lead"),
        (STAGE_PROPOSAL, "Proposal"),
        (STAGE_WON, "Won"),
        (STAGE_LOST, "Lost"),
    ]

    title = models.CharField(max_length=200)
    contact = models.ForeignKey(
        Contact, on_delete=models.SET_NULL, null=True, blank=True, related_name="deals"
    )
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default=STAGE_LEAD)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title


class Activity(models.Model):
    """A logged interaction: call, email, meeting, note."""

    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="activities")
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Note on {self.contact} ({self.created_at:%Y-%m-%d})"


class ConsentLog(models.Model):
    """
    Append-only record of every consent change for a contact — required to
    demonstrate GDPR Article 7 compliance (being able to show how and when
    consent was obtained or withdrawn).
    """

    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="consent_logs")
    status = models.CharField(max_length=20, choices=Contact.CONSENT_CHOICES)
    source = models.CharField(
        max_length=150, help_text="How consent was captured, e.g. signup form, phone call"
    )
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at"]

    def __str__(self):
        return f"{self.contact} -> {self.status} ({self.recorded_at:%Y-%m-%d})"


class AuditLog(models.Model):
    """
    Append-only record of who accessed or changed personal data, and when.
    This is the backbone of your GDPR accountability story (Article 5(2)).
    """

    ACTION_VIEW = "view"
    ACTION_CREATE = "create"
    ACTION_UPDATE = "update"
    ACTION_EXPORT = "export"
    ACTION_ERASE = "erase"
    ACTION_CHOICES = [
        (ACTION_VIEW, "Viewed"),
        (ACTION_CREATE, "Created"),
        (ACTION_UPDATE, "Updated"),
        (ACTION_EXPORT, "Exported"),
        (ACTION_ERASE, "Erased"),
    ]

    contact = models.ForeignKey(
        Contact, on_delete=models.SET_NULL, null=True, related_name="audit_entries"
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    performed_by = models.CharField(max_length=150, default="system")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.action} on {self.contact} at {self.timestamp:%Y-%m-%d %H:%M}"
