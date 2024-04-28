# external import
import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles


# internal import
from routers.templateRoutes import templateRoutes

app = FastAPI(
    title="An Interactive deshboard for Twitter",
    description="Assignment of Cloud Platforms & Applications",
)


# static and template files are defined
app.mount("/static", StaticFiles(directory="static"), name="static")


# ** Template Routes
app.include_router(templateRoutes)


if __name__ == "__main__":
    uvicorn.run("main:app", port=4000, reload=True, log_level="info")
