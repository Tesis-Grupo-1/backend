from fastapi import FastAPI
from app.database import init_db, close_db
from app.api import auth_router


async def lifespan(app: FastAPI):
    # Evento de startup
    await init_db()
    yield  # Esto indica que el servidor está en funcionamiento
    # Evento de shutdown
    await close_db()
    
    
app = FastAPI(title="MinaScan", version="0.1.0", lifespan=lifespan)


app.include_router(auth_router, prefix="/auth", tags=["auth"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)