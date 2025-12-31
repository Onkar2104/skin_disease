from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
# from .models import StudentProfile
from .forms import UserAdminCreationForm, UserAdminChangeForm

class UserAdmin(BaseUserAdmin):
    search_fields = ['email', 'full_name', 'phone', 'age', 'gender', 'skin_type']
    form = UserAdminChangeForm 
    add_form = UserAdminCreationForm 

    list_display = ['email', 'is_staff', 'is_active', 'is_superuser']

    fieldsets = (
        ('Personal Info', {'fields': ('full_name', 'phone', 'email', 'age', 'gender', 'skin_type', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('full_name', 'phone', 'email', 'age', 'gender', 'skin_type', 'password', 'password_2', 'is_staff', 'is_active'),
        }),
    )

    ordering = ['email']  


admin.site.register(User, UserAdmin)