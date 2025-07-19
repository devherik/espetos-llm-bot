import os
from utils.logger import log_message
from data_ingestor.data_ingestor_imp import DataIngestor
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.concurrency import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize resources or connections here if needed
    await startup_event(app)
    yield
    await shutdown_event(app)
    # Clean up resources or connections here if needed

app = FastAPI(lifespan=lifespan)
database = DataIngestor()


async def startup_event(app: FastAPI) -> None:
    # Perform startup tasks here, like loading models or initializing services
    log_message("Application is starting up...", "INFO")
    await database.initialize()
    app.state.some_resource = "Resource Initialized"


async def shutdown_event(app: FastAPI) -> None:
    # Perform shutdown tasks here, like closing connections or saving state
    log_message("Application is shutting down...", "INFO")
    app.state.some_resource = None


@app.get("/")
async def read_root(request: Request):
    await database.reload_data()
    return {
        "message": "Welcome to the Oracle API",
        "resource": request.app.state.some_resource
    }
