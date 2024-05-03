# external import
from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates


# internal import


templateRoutes = APIRouter()
templates = Jinja2Templates(directory="templates")


@templateRoutes.get("/")
async def home_page(req: Request):

    try:
        user_info = req.state.user_info

        if len(user_info) == 0:
            return RedirectResponse("/login")

    except:
        return RedirectResponse("/login")

    return templates.TemplateResponse(request=req, name="home.html")


@templateRoutes.get("/profile")
async def home_page(req: Request):

    try:
        user_info = req.state.user_info

        if len(user_info) == 0:
            return RedirectResponse("/login")

    except:
        return RedirectResponse("/login")

    return templates.TemplateResponse(request=req, name="profile.html")


@templateRoutes.get("/search")
async def home_page(req: Request):

    try:
        user_info = req.state.user_info

        if len(user_info) == 0:
            return RedirectResponse("/login")

    except:
        return RedirectResponse("/login")

    return templates.TemplateResponse(request=req, name="search.html")


@templateRoutes.get("/login")
async def login_page(req: Request):
    return templates.TemplateResponse(request=req, name="login.html")


@templateRoutes.get("/signup")
async def login_page(req: Request):
    return templates.TemplateResponse(request=req, name="signup.html")
