import os
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


async def startup_event(app: FastAPI) -> None:
    # Perform startup tasks here, like loading models or initializing services
    print("---> Application is starting up...")
    app.state.some_resource = "Resource Initialized"


async def shutdown_event(app: FastAPI) -> None:
    # Perform shutdown tasks here, like closing connections or saving state
    print("---> Application is shutting down...")
    app.state.some_resource = None


@app.get("/")
async def read_root(request: Request):
    return {"message": "Welcome to the Oracle API", "resource": request.app.state.some_resource}
