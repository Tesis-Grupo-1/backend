from tortoise import fields, models

class Detection(models.Model):
    id_detection = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="detections", on_delete=fields.CASCADE)
    field = fields.ForeignKeyField("models.Field", related_name="detections", on_delete=fields.CASCADE)
    date_detection = fields.DateField()
    time_initial = fields.TimeField()
    time_final = fields.TimeField()
    prediction_value = fields.CharField(max_length=255)
    result = fields.CharField(max_length=255)
    plague_percentage = fields.FloatField()
    created_at = fields.DatetimeField(auto_now_add=True)

    # 👇 Una detección puede tener muchas imágenes
    images: fields.ReverseRelation["Images"]

    def __str__(self):
        return f"Detection {self.id_detection} - {self.result}"

    class Meta:
        table = "detection"