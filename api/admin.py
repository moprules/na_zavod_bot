from django.contrib import admin

# Register your models here.
from .models import Chat
# admin.site.register(Chat)

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'is_online', 'is_send')