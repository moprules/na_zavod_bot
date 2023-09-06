from django.db import models

# Create your models here.
class Chat(models.Model):
    chat_id = models.IntegerField(primary_key=True)
