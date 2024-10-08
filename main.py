from fastapi import FastAPI
from routes import log_routes, screen_routes, utils_routes, llm_routes, training_model_routes
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from middleware.utils_llm import generate_text_model_to_llm_in_file
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    generate_text_model_to_llm_in_file(False)
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(training_model_routes.router)
app.include_router(log_routes.router)
app.include_router(screen_routes.router)
app.include_router(utils_routes.router)
app.include_router(llm_routes.router)

# UI Configuration
templates = Jinja2Templates(directory="ui/templates")
app.mount("/static", StaticFiles(directory="ui/statics"), name="static")