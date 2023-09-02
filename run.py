import uvicorn
from app.main import app
from app.core.config import settings

uvicorn.run(app, host=settings.app.host, port=settings.app.port)
