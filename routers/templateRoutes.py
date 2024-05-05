# external import
from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates


# internal import
from routers.twitterRoutes import get_user_info, search_tweet, search_users

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

    user = await get_user_info(user_info["user_id"])

    if user:

        return templates.TemplateResponse(
            request=req,
            name="home.html",
            context={"user_id": user_info["user_id"], "user_data": user},
        )
    else:
        return RedirectResponse("/get_username")


@templateRoutes.get("/profile")
async def home_page(req: Request, user_id: str):

    try:
        user_info = req.state.user_info

        if len(user_info) == 0:
            return RedirectResponse("/login")

        user = await get_user_info(user_id, user_info['user_id'])

    except:
        return RedirectResponse("/login")

    return templates.TemplateResponse(
        request=req,
        name="profile.html",
        context={
            "user_id": user_info["user_id"],
            "user_data": user,
            "tweet_posts": user["tweets"][:-11:-1],
        },
    )


@templateRoutes.get("/search")
async def home_page(
    req: Request,
    user_search_value: str | None = None,
    tweet_search_value: str | None = None,
):

    user_data = None
    tweet_posts = None

    try:
        user_info = req.state.user_info

        if len(user_info) == 0:
            return RedirectResponse("/login")

        if user_search_value:
            user_data = await search_users(user_search_value)

        if tweet_search_value:
            tweet_posts = await search_tweet(tweet_search_value)

        return templates.TemplateResponse(
            request=req,
            name="search.html",
            context={
                "user_id": user_info["user_id"],
                "user_data": user_data,
                "tweet_posts": tweet_posts,
            },
        )

    except Exception as e:
        print(e)
        return RedirectResponse("/login")


@templateRoutes.get("/setting")
async def home_page(req: Request):

    try:
        user_info = req.state.user_info

        if len(user_info) == 0:
            return RedirectResponse("/login")

    except:
        return RedirectResponse("/login")

    return templates.TemplateResponse(
        request=req,
        name="setting.html",
        context={"user_id": user_info["user_id"]},
    )


@templateRoutes.get("/get_username")
async def home_page(req: Request):

    try:
        user_info = req.state.user_info

        if len(user_info) == 0:
            return RedirectResponse("/login")

    except:
        return RedirectResponse("/login")

    return templates.TemplateResponse(request=req, name="get-username.html")


@templateRoutes.get("/login")
async def login_page(req: Request):
    return templates.TemplateResponse(request=req, name="login.html")


@templateRoutes.get("/signup")
async def login_page(req: Request):
    return templates.TemplateResponse(request=req, name="signup.html")
