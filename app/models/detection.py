from tortoise import fields, models

class Detection(models.Model):
    id_detection = fields.IntField(pk=True)
    image = fields.ForeignKeyField("models.Images", related_name="detection", on_delete=fields.CASCADE)
    date_detection = fields.DatetimeField(auto_now_add=True)
    time_initial = fields.CharField(max_length=255, null=True)
    time_final = fields.CharField(max_length=255, null=True)
    time_detection = fields.FloatField(null=True)
    prediction_value = fields.CharField(max_length=255)
    result = fields.CharField(max_length=255)

    def __str__(self):
        return f"Detection {self.id_detection} - {self.result}"

    class Meta:
        table = "detection"