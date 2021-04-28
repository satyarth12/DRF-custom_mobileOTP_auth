from __future__ import unicode_literals
from django.contrib.auth import get_user_model
from django.contrib import admin

from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import PhoneOTP

admin.site.register(PhoneOTP)


User = get_user_model()
class UserAdmin(admin.ModelAdmin):
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('name', 'phone',  'standard',  'is_admin')
    list_filter = ('standard','is_staff','is_active' ,'is_admin', )
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Personal info', {'fields': ('name', 'standard','score',)}),
        ('Permissions', {'fields': ('is_admin','is_staff','is_active')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'password1', 'password2')}
        ),
    )


    search_fields = ('phone','name')
    ordering = ('phone','name')
    filter_horizontal = ()



admin.site.register(User, UserAdmin)



# Remove Group Model from admin. We're not using it.
admin.site.unregister(Group)