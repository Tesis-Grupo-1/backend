from tortoise import fields, models
from cryptography.fernet import Fernet
from app.core import settings
import base64

class Report(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="reports", on_delete=fields.CASCADE)
    field = fields.ForeignKeyField("models.Field", related_name="reports", on_delete=fields.CASCADE)
    detection = fields.ForeignKeyField("models.Detection", related_name="reports", on_delete=fields.CASCADE)
    title = fields.CharField(max_length=200)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    # Campos cifrados
    _content = fields.TextField()  # Contenido del reporte cifrado
    _ai_generated_content = fields.TextField(null=True)  # Contenido generado por IA cifrado
    _pdf_path = fields.TextField(null=True)  # Ruta del PDF cifrado
    
    def __str__(self):
        return f"Report {self.title} - {self.user.email}"
    
    @property
    def content(self):
        if self._content:
            return self._decrypt_data(self._content)
        return None
    
    @content.setter
    def content(self, value):
        if value:
            self._content = self._encrypt_data(value)
        else:
            self._content = None
    
    @property
    def ai_generated_content(self):
        if self._ai_generated_content:
            return self._decrypt_data(self._ai_generated_content)
        return None
    
    @ai_generated_content.setter
    def ai_generated_content(self, value):
        if value:
            self._ai_generated_content = self._encrypt_data(value)
        else:
            self._ai_generated_content = None
    
    @property
    def pdf_path(self):
        if self._pdf_path:
            return self._decrypt_data(self._pdf_path)
        return None
    
    @pdf_path.setter
    def pdf_path(self, value):
        if value:
            self._pdf_path = self._encrypt_data(value)
        else:
            self._pdf_path = None
    
    def _encrypt_data(self, data: str) -> str:
        """Cifra datos sensibles"""
        fernet = Fernet(settings.ENCRYPTION_KEY.encode())
        return fernet.encrypt(data.encode()).decode()
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Descifra datos sensibles"""
        fernet = Fernet(settings.ENCRYPTION_KEY.encode())
        return fernet.decrypt(encrypted_data.encode()).decode()
    
    class Meta:
        table = "reports"
