from tortoise import fields, models
from cryptography.fernet import Fernet
from app.core import settings
import base64

class Field(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    size_hectares = fields.FloatField()
    user = fields.ForeignKeyField("models.User", related_name="fields", on_delete=fields.CASCADE)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    # Campos cifrados
    _location = fields.TextField()  # Coordenadas cifradas
    _description = fields.TextField(null=True)  # Descripción cifrada
    
    def __str__(self):
        return f"Field {self.name} - {self.size_hectares} ha"
    
    @property
    def location(self):
        if self._location:
            try:
                return self._decrypt_data(self._location)
            except Exception:
                # Si hay error al descifrar, devolver el valor sin cifrar (para compatibilidad)
                return self._location
        return None
    
    @location.setter
    def location(self, value):
        if value:
            self._location = self._encrypt_data(value)
        else:
            self._location = None
    
    @property
    def description(self):
        if self._description:
            try:
                return self._decrypt_data(self._description)
            except Exception:
                # Si hay error al descifrar, devolver el valor sin cifrar (para compatibilidad)
                return self._description
        return None
    
    @description.setter
    def description(self, value):
        if value:
            self._description = self._encrypt_data(value)
        else:
            self._description = None
    
    def _encrypt_data(self, data: str) -> str:
        """Cifra datos sensibles"""
        fernet = Fernet(settings.ENCRYPTION_KEY.encode())
        return fernet.encrypt(data.encode()).decode()
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Descifra datos sensibles"""
        fernet = Fernet(settings.ENCRYPTION_KEY.encode())
        return fernet.decrypt(encrypted_data.encode()).decode()
    
    class Meta:
        table = "fields"
