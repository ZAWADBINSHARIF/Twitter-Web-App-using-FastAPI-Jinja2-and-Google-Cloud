# external import
from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates


# internal import


templateRoutes = APIRouter()
templates = Jinja2Templates(directory="templates")


@templateRoutes.get("/")
async def home_page(req: Request):
    return templates.TemplateResponse(request=req, name="home.html")


@templateRoutes.get("/profile")
async def home_page(req: Request):
    return templates.TemplateResponse(request=req, name="profile.html")


@templateRoutes.get("/login")
async def login_page(req: Request):
    return templates.TemplateResponse(request=req, name="login.html")
