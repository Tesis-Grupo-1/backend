from app.models import User


class UserRepository:
    
    @staticmethod
    async def create_user(data):
        user = await User.create(**data)
        return user

    @staticmethod
    async def get_user_by_email(email: str):
        
        user = await User.get_or_none(email=email)
        return user
        