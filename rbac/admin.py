from django.contrib import admin
from .models import Role, Membership, AuditEntry


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'permission_count']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['permissions']

    def permission_count(self, obj):
        """Show how many permissions this role has."""
        return obj.permissions.count()
    
    permission_count.short_description = 'Permissions'
    
@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__username', 'user__email', 'role__name']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Role Assignment', {
            'fields': ('user', 'role')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']

    def get_queryset(self, request):
        """Optimize queries by selecting related user and role"""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'role')

@admin.register(AuditEntry)
class AuditEntryAdmin(admin.ModelAdmin):
    list_display = ['actor', 'action', 'timestamp', 'target_type', 'organization']
    list_filter = ['action', 'timestamp', 'target_content_type', 'organization']
    search_fields = ['actor__username', 'payload']
    date_hierarchy = 'timestamp'
    readonly_fields = ['actor', 'action', 'target_content_type', 'target_object_id', 'timestamp', 'payload', 'organization']

    def target_type(self, obj):
        """Show what type of object was affected"""
        return obj.target_content_type.model

    target_type.short_description = 'Target Type'

    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj = ...):
        return False
    
    def get_queryset(self, request):
        """Optimize queries"""
        qs = super().get_queryset(request)
        return qs.select_related('actor', 'target_content_type', 'organization')
    