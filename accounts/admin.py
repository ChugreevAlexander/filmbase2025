from django.contrib import admin
from django.contrib.auth.models import User
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'birthday')
    search_fields = ('user__username', 'user__email')