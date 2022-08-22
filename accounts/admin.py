from django.contrib import admin

from .models import Account, UserProfile
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html


class AccountAdmin(UserAdmin):
    list_display = ['first_name', 'last_name', 'username',
                    'email', 'last_login', 'date_joined', 'is_active']
    list_display_links = ['first_name', 'last_name']
    readonly_fields = ['last_login', 'date_joined', ]
    ordering = ['-date_joined']

    filter_horizontal = ()
    fieldsets = ()
    list_filter = ()


class UserProfileAdmin(admin.ModelAdmin):
    # def thumbnail(self, object):
    #     return format_html('<img  src="{}" width="30px" style="border-radius:50%" >'.format(object.profile_picture.url))
    # thumbnail.short_description = "Profile Picture"

    list_display = ["user", "city", "state", "country"]


# Register your models here.
admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
