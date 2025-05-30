from fastapi import FastAPI
from app.database import init_db, close_db
from app.api import photo_router, detection_router
from app.core import settings

  

async def lifespan(app: FastAPI):

    try:
        await init_db()
        yield
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")
    finally:
        await close_db()
     
    
app = FastAPI(title="MinaScan", version="0.1.0", lifespan=lifespan)


app.include_router(photo_router, prefix="/photo", tags=["photo"])
app.include_router(detection_router, prefix="/detection", tags=["detection"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT, reload=True)