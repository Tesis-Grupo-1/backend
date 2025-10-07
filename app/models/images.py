from tortoise import fields, models

class Images(models.Model):
    id_image = fields.IntField(pk=True)
    detection = fields.ForeignKeyField(
        "models.Detection",
        related_name="images",
        on_delete=fields.CASCADE,
        null=True  
    )

    image_path = fields.CharField(max_length=255)
    porcentaje_plaga = fields.FloatField()
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id_image} - {self.url_image}"

    class Meta:
        table = "images"