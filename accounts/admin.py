from django.contrib import admin
from .models import Profile
# Register your models here.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user",)
    search_fields = ("user__username", "user__email")