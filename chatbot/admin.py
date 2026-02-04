from django.contrib import admin
from .models import DigitalIdentity, Complaint


@admin.register(DigitalIdentity)
class DigitalIdentityAdmin(admin.ModelAdmin):
    list_display = ('user', 'digital_id', 'created_at')
    search_fields = ('user__username', 'digital_id')
    readonly_fields = ('digital_id', 'created_at')


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = (
        'department',
        'issue_type',
        'priority',
        'status',
        'created_at'
    )
    list_filter = ('department', 'priority', 'status')
    search_fields = ('issue_type', 'description')
    ordering = ('-created_at',)
