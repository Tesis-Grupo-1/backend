import os, dotenv
from tortoise import fields, models

dotenv.load_dotenv()

class Images(models.Model):
    id_image = fields.IntField(pk=True)
    
    user = fields.ForeignKeyField("models.User", related_name="images", on_delete=fields.CASCADE)
    url_image = fields.CharField(max_length=255, unique=True)
    upload_Date = fields.DatetimeField(auto_now_add=True)
    crop = fields.CharField(max_length=255)

    def __str__(self):
        return self.id_image

    class Meta:
        table = "images"