from tortoise import fields, models

class Detection(models.Model):
    id_detection = fields.IntField(pk=True)
    image = fields.ForeignKeyField("models.Images", related_name="detection", on_delete=fields.CASCADE)
    date_detection = fields.DateField()
    time_initial = fields.TimeField()
    time_final = fields.TimeField()
    prediction_value = fields.CharField(max_length=255)
    result = fields.CharField(max_length=255)

    def __str__(self):
        return f"Detection {self.id_detection} - {self.result}"

    class Meta:
        table = "detection"