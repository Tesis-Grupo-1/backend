from app.models import Images

class ImageRepository:
    
    @staticmethod
    async def create_image(url_image: str, name: str) -> Images:
        """
        Crea una nueva imagen en la base de datos.
        """
        image = await Images.create(url_image=url_image, name=name)
        return image
    
    @staticmethod
    async def get_image_by_id(image_id: int) -> Images:
        """
        Obtiene una imagen por su ID.
        """
        image = await Images.get_or_none(id_image=image_id)
        return image