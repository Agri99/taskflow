from django.contrib import admin
from .models import Role, Membership, AuditEntry


class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['permissions']

class AuditEntryAdmin(admin.ModelAdmin):
    list_display = ['actor', 'action', 'timestamp', 'target_content_type']
    readonly_fields = ['actor', 'action', 'target_content_type', 'target_object_id', 'timestamp', 'payload', 'organization']

    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj = ...):
        return False
    
    def has_change_permission(self, request, obj = ...):
        return True


admin.site.register(Role, RoleAdmin)
admin.site.register(Membership)
admin.site.register(AuditEntry, AuditEntryAdmin)