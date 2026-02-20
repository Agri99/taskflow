from django.contrib import admin
from .models import Organization, MembershipProfile


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(MembershipProfile)
class MembershipProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'organization', 'role', 'created_at']
    list_filter = ['role', 'organization']
    search_fields = ['user__username', 'organization__name']
    
    # Make it clear what you're doing
    fieldsets = (
        ('User Assignment', {
            'fields': ('user', 'organization', 'role')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']