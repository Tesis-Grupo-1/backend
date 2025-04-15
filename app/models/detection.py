from tortoise import fields, models

class Detection(models.Model):
    id_detection = fields.IntField(pk=True)
    
    image = fields.ForeignKeyField("models.Images", related_name="detection", on_delete=fields.CASCADE)
    date_detection = fields.DatetimeField(auto_now_add=True)
    result = fields.CharField(max_length=255)

    def __str__(self):
        return self.id_detection

    class Meta:
        table = "detection"