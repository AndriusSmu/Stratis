#!/usr/bin/env python
"""
Development server runner.
"""

import uvicorn

from app.config import config

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=config.api.host,
        port=config.api.port,
        reload=config.api.reload,
        log_level="info",
    )
