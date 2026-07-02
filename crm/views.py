import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import AuditLog, Contact, Deal


def _actor(request):
    return request.user.username


def _is_admin(request):
    profile = getattr(request.user, "profile", None)
    return bool(profile and profile.is_admin)


@login_required
def dashboard(request):
    contacts_count = Contact.objects.count()
    open_deals = Deal.objects.exclude(stage__in=[Deal.STAGE_WON, Deal.STAGE_LOST]).count()
    pipeline_value = sum(
        d.value for d in Deal.objects.exclude(stage__in=[Deal.STAGE_WON, Deal.STAGE_LOST])
    )
    granted = Contact.objects.filter(consent_status=Contact.CONSENT_GRANTED).count()
    consent_rate = round((granted / contacts_count) * 100) if contacts_count else 0

    stages = [Deal.STAGE_LEAD, Deal.STAGE_PROPOSAL, Deal.STAGE_WON]
    pipeline = {stage: Deal.objects.filter(stage=stage).select_related("contact") for stage in stages}

    context = {
        "contacts_count": contacts_count,
        "open_deals": open_deals,
        "pipeline_value": pipeline_value,
        "consent_rate": consent_rate,
        "pipeline": pipeline,
        "recent_audit": AuditLog.objects.select_related("contact")[:6],
    }
    return render(request, "crm/dashboard.html", context)


@login_required
def contact_list(request):
    contacts = Contact.objects.all()
    return render(request, "crm/contacts.html", {"contacts": contacts})


@login_required
def contact_detail(request, pk):
    contact = get_object_or_404(Contact, pk=pk)

    if request.method == "POST":
        action = request.POST.get("action")

        if action in ("export", "erase") and not _is_admin(request):
            raise PermissionDenied("Only admins can export or erase contact data.")

        if action == "export":
            AuditLog.objects.create(contact=contact, action=AuditLog.ACTION_EXPORT, performed_by=_actor(request))
            data = {
                "name": contact.full_name,
                "email": contact.email,
                "phone": contact.phone,
                "company": contact.company,
                "role": contact.role,
                "consent_status": contact.consent_status,
                "created_at": contact.created_at.isoformat(),
                "consent_history": [
                    {"status": log.status, "source": log.source, "recorded_at": log.recorded_at.isoformat()}
                    for log in contact.consent_logs.all()
                ],
            }
            response = HttpResponse(
                json.dumps(data, indent=2), content_type="application/json"
            )
            filename = f"{contact.full_name.replace(' ', '_')}_data_export.json"
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response

        if action == "erase":
            contact.first_name = "Redacted"
            contact.last_name = "Redacted"
            contact.email = f"erased-{contact.pk}@redacted.local"
            contact.phone = ""
            contact.company = ""
            contact.role = ""
            contact.is_anonymised = True
            contact.consent_status = Contact.CONSENT_WITHDRAWN
            contact.save()
            AuditLog.objects.create(contact=contact, action=AuditLog.ACTION_ERASE, performed_by=_actor(request))
            messages.success(request, "Contact data anonymised in line with the right to erasure.")
            return redirect("contact_list")

    AuditLog.objects.create(contact=contact, action=AuditLog.ACTION_VIEW, performed_by=_actor(request))
    context = {
        "contact": contact,
        "activities": contact.activities.all(),
        "consent_logs": contact.consent_logs.all(),
    }
    return render(request, "crm/contact_detail.html", context)


@login_required
def deal_list(request):
    stages = [Deal.STAGE_LEAD, Deal.STAGE_PROPOSAL, Deal.STAGE_WON, Deal.STAGE_LOST]
    pipeline = {stage: Deal.objects.filter(stage=stage).select_related("contact") for stage in stages}
    return render(request, "crm/deals.html", {"pipeline": pipeline})
