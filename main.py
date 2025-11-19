"""
NEXXBot Application Entry Point
"""

import uvicorn
from nexxbot.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "nexxbot.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
