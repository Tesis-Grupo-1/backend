from tortoise import Tortoise
from app.core import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_db():
    try:
        await Tortoise.init(
            db_url=settings.DATABASE_URL, 
            modules={"models": ["app.models"]},
        )
        await Tortoise.generate_schemas()
        logger.info("Base de datos conectada y esquemas generados con éxito.")
    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {e}")
        raise  
    
async def close_db():
    try:
        await Tortoise.close_connections()
        logger.info("Conexiones a la base de datos cerradas correctamente.")
    except Exception as e:
        logger.error(f"Error al cerrar las conexiones de la base de datos: {e}") 
