from django.db import models

# Create your models here.
class Chat(models.Model):
    chat_id = models.IntegerField(primary_key=True, verbose_name="ID чата в телеграмме")
    is_online = models.BooleanField(default=True, verbose_name="Статус онлайна пользователя")
    is_send = models.BooleanField(default=True, verbose_name="Отправляли уведомление")
    
