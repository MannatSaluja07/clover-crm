from django.contrib import admin

from .models import Activity, AuditLog, ConsentLog, Contact, Deal, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    list_filter = ("role",)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "company", "consent_status", "is_anonymised")
    list_filter = ("consent_status", "is_anonymised")
    search_fields = ("first_name", "last_name", "email", "company")


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ("title", "contact", "value", "stage", "updated_at")
    list_filter = ("stage",)
    search_fields = ("title",)


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("contact", "created_at")


@admin.register(ConsentLog)
class ConsentLogAdmin(admin.ModelAdmin):
    list_display = ("contact", "status", "source", "recorded_at")
    list_filter = ("status",)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "contact", "performed_by", "timestamp")
    list_filter = ("action",)
    readonly_fields = ("contact", "action", "performed_by", "timestamp")

    def has_add_permission(self, request):
        # Audit entries should only ever be created by the app itself.
        return False

    def has_delete_permission(self, request, obj=None):
        return False
