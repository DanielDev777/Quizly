from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from auth_app.models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'is_staff', 'created_at')
    list_filter = ('is_staff', 'is_superuser', 'created_at')
    search_fields = ('email', 'username')
    ordering = ('-created_at',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')