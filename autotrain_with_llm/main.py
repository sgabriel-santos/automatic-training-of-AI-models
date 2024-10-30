from fastapi import FastAPI
from autotrain_with_llm.routes import log_routes, screen_routes, utils_routes, llm_routes, training_model_routes
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from autotrain_with_llm.middleware.utils_llm import generate_text_model_to_llm_in_file
from contextlib import asynccontextmanager
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    generate_text_model_to_llm_in_file(0)
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(training_model_routes.router)
app.include_router(log_routes.router)
app.include_router(screen_routes.router)
app.include_router(utils_routes.router)
app.include_router(llm_routes.router)

# UI Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(BASE_DIR, "ui/statics")
templates_path = os.path.join(BASE_DIR, "ui/templates")
templates = Jinja2Templates(directory=templates_path)
app.mount("/static", StaticFiles(directory=static_path), name="static")