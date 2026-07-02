# Data protection notes

This CRM is a portfolio project built to demonstrate GDPR / Irish Data
Protection Act 2018 awareness, not a certified compliance product. Below is
what it does and why, in the language you'd use to talk about it in an
interview.

## What personal data is processed
Name, email, phone, company, and role for business contacts, plus free-text
notes logged by sales staff.

## Legal basis
Consent (Article 6(1)(a)) — captured and tracked per contact via
`consent_status` and the append-only `ConsentLog` model.

## Rights implemented
- **Right of access / portability** (Art. 15/20): contact detail page →
  "Export data (JSON)".
- **Right to erasure** (Art. 17): contact detail page → "Erase personal
  data" — anonymises identifying fields rather than hard-deleting the row,
  so deal history and audit trail remain intact without exposing PII.
- **Accountability** (Art. 5(2)): every view, export, and erase action is
  written to the `AuditLog` model, showing who accessed what and when.

## Data retention
`DATA_RETENTION_MONTHS` in `settings.py` documents the intended retention
window. A scheduled job (e.g. `django-crontab` or Celery beat, not yet
wired up) would flag or anonymise contacts with no activity past that
window — this is a good "what would you add next" talking point.

## What a real production deployment would still need
- A published privacy notice and cookie policy
- A Data Processing Record (Article 30) covering any third-party
  processors (email provider, hosting)
- A Data Protection Impact Assessment if processing at scale
- Signed Data Processing Agreements with any sub-processors
- TLS everywhere, encrypted database backups, and access logging at the
  infrastructure level (not just the application level)
