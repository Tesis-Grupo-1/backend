from tortoise import fields, models
from enum import Enum
from cryptography.fernet import Fernet
from app.core import settings
import base64

class UserRole(str, Enum):
    EMPLOYEE = "employee"
    BOSS = "boss"

class User(models.Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=100, unique=True)
    hashed_password = fields.CharField(max_length=255)
    full_name = fields.CharField(max_length=100)
    role = fields.CharEnumField(UserRole, default=UserRole.EMPLOYEE)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    # Relación jefe-empleado
    boss = fields.ForeignKeyField("models.User", related_name="employees", null=True, on_delete=fields.SET_NULL)
    linking_code = fields.CharField(max_length=10, unique=True, null=True)  # Código para vincular empleados
    
    
    def __str__(self):
        return f"User {self.email} - {self.role}"
    
    
    def _encrypt_data(self, data: str) -> str:
        """Cifra datos sensibles"""
        key = base64.urlsafe_b64decode(settings.ENCRYPTION_KEY.encode())
        fernet = Fernet(key)
        return fernet.encrypt(data.encode()).decode()
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Descifra datos sensibles"""
        key = base64.urlsafe_b64decode(settings.ENCRYPTION_KEY.encode())
        fernet = Fernet(key)
        return fernet.decrypt(encrypted_data.encode()).decode()
    
    class Meta:
        table = "users"
