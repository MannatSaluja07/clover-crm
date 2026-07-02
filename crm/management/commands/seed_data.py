from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from crm.models import Activity, ConsentLog, Contact, Deal, UserProfile


class Command(BaseCommand):
    help = "Populate the database with sample CRM data and demo users for local demos."

    def handle(self, *args, **options):
        self._seed_users()

        if Contact.objects.exists():
            self.stdout.write(self.style.WARNING("Contact data already exists, skipping seed."))
            return

        contacts_data = [
            ("Aoife", "Byrne", "aoife.byrne@kelleherlogistics.ie", "Kelleher Logistics", "granted"),
            ("Sean Og", "Murphy", "so.murphy@fingalmfg.ie", "Fingal Manufacturing", "pending"),
            ("Niamh", "O'Connor", "niamh.oconnor@corkfreight.ie", "Cork Freight Co", "withdrawn"),
            ("Cian", "Walsh", "cian.walsh@dlretail.ie", "Dun Laoghaire Retail", "granted"),
            ("Roisin", "Kelly", "roisin.kelly@galwayhealth.ie", "Galway Health Group", "granted"),
        ]

        contacts = []
        for first, last, email, company, consent in contacts_data:
            contact = Contact.objects.create(
                first_name=first,
                last_name=last,
                email=email,
                company=company,
                consent_status=consent,
            )
            ConsentLog.objects.create(
                contact=contact, status=consent, source="signup form"
            )
            Activity.objects.create(
                contact=contact, note=f"Initial call with {first} to introduce the product."
            )
            contacts.append(contact)

        deals_data = [
            ("Kelleher Logistics - fleet contract", contacts[0], 18000, Deal.STAGE_LEAD),
            ("Dun Laoghaire Retail - POS rollout", contacts[3], 9500, Deal.STAGE_LEAD),
            ("Fingal Manufacturing - annual license", contacts[1], 52000, Deal.STAGE_PROPOSAL),
            ("Cork Freight - route optimiser", contacts[2], 31200, Deal.STAGE_PROPOSAL),
            ("Galway Health - support package", contacts[4], 27000, Deal.STAGE_WON),
        ]
        for title, contact, value, stage in deals_data:
            Deal.objects.create(title=title, contact=contact, value=value, stage=stage)

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(contacts)} contacts and {len(deals_data)} deals."))

    def _seed_users(self):
        demo_users = [
            ("demo_admin", UserProfile.ROLE_ADMIN),
            ("demo_sales", UserProfile.ROLE_SALES),
            ("demo_manager", UserProfile.ROLE_MANAGER),
        ]
        for username, role in demo_users:
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password("demopass123")
                user.save()
            UserProfile.objects.get_or_create(user=user, defaults={"role": role})
        self.stdout.write(self.style.SUCCESS(
            "Demo users ready: demo_admin / demo_sales / demo_manager, password 'demopass123' for all."
        ))
