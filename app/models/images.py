from tortoise import fields, models

class Images(models.Model):
    id_image = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    url_image = fields.CharField(max_length=255, unique=True)
    upload_Date = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id_image} - {self.url_image}"

    class Meta:
        table = "images"