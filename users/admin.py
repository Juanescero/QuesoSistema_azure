from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Proveedor

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'documento', 'primer_nombre', 'primer_apellido', 'is_staff', 'is_active', 'last_login', 'list_groups')
    list_filter = ('is_staff', 'is_active', 'groups')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('documento', 'primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido', 'telefono', 'imagen')}),
        ('Permisos', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'documento', 'primer_nombre', 'primer_apellido', 'password1', 'password2', 'is_staff', 'is_active', 'groups')}
        ),
    )
    search_fields = ('email', 'documento', 'primer_nombre', 'primer_apellido')
    ordering = ('email',)

    def list_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    list_groups.short_description = 'Grupos'

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Proveedor)
