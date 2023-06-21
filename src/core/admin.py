from django.contrib import admin
from .models import AdditionalUser, UpcomingCall

# Register your models here.

@admin.register(AdditionalUser)
class AdditionalUserAdmin(admin.ModelAdmin):
    list_display = ('time_zone', )
    list_filter = ('user',)

@admin.register(UpcomingCall)
class UpcomingCallAdmin(admin.ModelAdmin):
    list_display = ('call_name', 'user', 'timestamp')
    list_filter = ('user',)
