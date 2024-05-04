# external import
import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from google.auth.transport import requests
import google.oauth2.id_token


# internal import
from routers.templateRoutes import templateRoutes
from routers.twitterRoutes import twitterRoutes

app = FastAPI(
    title="An Interactive deshboard for Twitter",
    description="Assignment of Cloud Platforms & Applications",
)


# static and template files are defined
app.mount("/static", StaticFiles(directory="static"), name="static")


firebase_request_adapter = requests.Request()


# ** Middleware
@app.middleware("http")
async def log_middleware(req: Request, call_next):

    id_token = req.cookies.get("token")

    if id_token and id_token != "":
        try:

            user_info = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter
            )
            req.state.user_info = user_info

        except Exception as err:
            print(err)
    else:
        req.state.user_info = {}

    response = await call_next(req)
    return response


# ** Template Routes
app.include_router(templateRoutes)
# ** Template Routes
app.include_router(twitterRoutes)


if __name__ == "__main__":
    uvicorn.run("main:app", port=4000, reload=True, log_level="info")
