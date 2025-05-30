from mcp_server_for_kagent.log import setup_logging

# logging must be setup before importing other modules
setup_logging()  # noqa: E402

import logging
import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from mcp_server_for_kagent.routers.alerts_fetcher import router as utilisationmail_router

log = logging.getLogger(__name__)

app = FastAPI(
    title="MCP SERVER FOR KAGENT",
    description="This is a FastAPI server for MCP Kagent",
    version="0.0.1",
)


@app.exception_handler(Exception)
def general_exception_handler(request: Request, exc: Exception):
    log.exception(msg="Uncaught error", exc_info=exc)

    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={})


app.include_router(utilisationmail_router)  # Router for Utilsation Mail


@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI!"}


# ATLAS-NOTIFICATIONS

if __name__ == "__main__":
    uvicorn.run("main:app", port=4337)
