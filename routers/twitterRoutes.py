# external import
from typing import Annotated
from fastapi import APIRouter, File, Request, UploadFile, Form
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.exceptions import HTTPException


# internal import
from config.databaseConnection import (
    db,
    firestore,
    bucket,
    storage,
    PROJECT_STORAGE_BUCKET,
)
from models.tweetModal import PostTweet


users_ref = db.collection("users")
tweets_ref = db.collection("tweets")


TW = twitterRoutes = APIRouter(prefix="/tw")


async def get_user_info(id: str):

    user = users_ref.document(id).get()

    return user


@TW.post("/set_profile_picture")
async def get_user(
    req: Request,
    file: Annotated[UploadFile, File()],
):

    try:
        user_info = req.state.user_info

        if len(user_info) == 0:
            return RedirectResponse("/login")

        blob = storage.Blob(name=file.filename, bucket=bucket)
        blob.upload_from_file(file.file)
        img_url = (
            "https://storage.cloud.google.com/"
            + PROJECT_STORAGE_BUCKET
            + "/"
            + file.filename
        )

        users_ref.document(user_info["user_id"]).update({"profile_img_url": img_url})

        return JSONResponse(
            content={"msg": "New profile image has been uploaded"}, status_code=200
        )

    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail={"error": "someting went wrong"})


@TW.post("/post")
async def get_user(
    req: Request,
    tweet: Annotated[str, Form()],
    tweet_type: Annotated[str, Form()],
    file: Annotated[UploadFile | None, File()] = None,
):

    try:
        user_info = req.state.user_info
        img_url = None

        if len(user_info) == 0:
            return RedirectResponse("/login")

        if file:
            blob = storage.Blob(name=file.filename, bucket=bucket)
            blob.upload_from_file(file.file)
            img_url = (
                "https://storage.cloud.google.com/"
                + PROJECT_STORAGE_BUCKET
                + "/"
                + file.filename
            )

        tweet_ref = tweets_ref.document()
        user_ref = users_ref.document(user_info["user_id"])

        tweet_ref.set(
            {
                "name": user_ref.get().to_dict().get("username"),
                "tweet": tweet,
                "type": tweet_type,
                "img_url": img_url,
                "user": user_ref,
            }
        )

        user_ref.update({"tweets": firestore.ArrayUnion([tweet_ref])})

        return JSONResponse(
            content={"msg": "New tweet has been uploaded"}, status_code=201
        )

    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail={"error": "someting went wrong"})


@TW.post("/set_username")
async def get_user(req: Request, username: str):

    try:
        user_info = req.state.user_info

        if len(user_info) == 0:
            return RedirectResponse("/login")

        all_users = users_ref.stream()

        for user in all_users:
            name = user.get("username")

            if name == username:
                return JSONResponse(
                    content={"error": "Same username exists"}, status_code=400
                )

        users_ref.document(user_info["user_id"]).set({"username": username})

        return JSONResponse(content={"msg": "username has been set"}, status_code=201)

    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"error": "someting went wrong"})
