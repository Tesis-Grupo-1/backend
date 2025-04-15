import os, dotenv
from tortoise import fields, models

dotenv.load_dotenv()

class User(models.Model):
    id_user = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    lastname = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255, unique=True)
    password = fields.CharField(max_length=255)
    date_register = fields.DateField(auto_now_add=True)

    def __str__(self):
        return self.id_user

    class Meta:
        table = "users"