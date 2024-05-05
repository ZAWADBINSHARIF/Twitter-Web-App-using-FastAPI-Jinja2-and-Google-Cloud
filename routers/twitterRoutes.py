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


users_ref = db.collection("users")
tweets_ref = db.collection("tweets")


TW = twitterRoutes = APIRouter(prefix="/tw")


async def search_tweet(tweet_value):
    try:

        tweets = tweets_ref.stream()
        tweets_array = []

        for tweet in tweets:
            tweet_doc = tweet.to_dict()
            tweet_doc["tweet_id"] = tweet.id

            post = tweet_doc["tweet"].lower()

            if post.startswith(tweet_value.lower()):
                user_dict = tweet_doc.get("user").get().to_dict()

                tweet_doc["user"] = user_dict

                tweets_array.append(tweet_doc)

        return tweets_array

    except Exception as e:
        print(e)


async def search_users(user_name_value):

    try:
        users = users_ref.get()

        search_value = []

        for user in users:
            username = user.get("username").lower()

            if username.startswith(user_name_value.lower()):

                value = user.to_dict()
                value["user_id"] = user.id

                search_value.append(value)

        return search_value

    except Exception as e:
        print(e)


async def get_last_limited_tweets(following_ref_array: list, own_user_id: str):

    count = 0
    latest_tweets = []

    try:
        query = tweets_ref.order_by(
            "date_and_time", direction=firestore.Query.DESCENDING
        )
        tweets = query.get()

        for tweet in tweets:
            for following_ref in following_ref_array:
                if (
                    tweet.to_dict().get("user") == following_ref
                    or tweet.to_dict().get("user") == users_ref.document(own_user_id)
                ) and count <= 20:
                    count = count + 1

                    tweet_data = tweet.to_dict()
                    tweet_data["user"] = tweet_data.get("user").get().to_dict()

                    latest_tweets.append(tweet_data)

                    if count == 20:
                        break

    except Exception as e:
        print(e)

    return latest_tweets


async def get_user_info(id: str, logged_in_user_id: str | None = None):

    try:
        user = users_ref.document(id).get()
        latest_tweets = []

        if user.exists:

            if logged_in_user_id == None:
                logged_in_user_id = id

            logged_in_user_dict = users_ref.document(logged_in_user_id).get().to_dict()

            user_dict = user.to_dict()
            user_dict["user_id"] = id
            tweets_array = []

            if user_dict.get("tweets"):
                tweets_ref_array = user.get("tweets")

                for tweet_ref in tweets_ref_array:
                    tweet = tweet_ref.get().to_dict()
                    tweet_user_info = tweet["user"].get().to_dict()
                    tweet_user_info["user_id"] = tweet["user"].id

                    tweet["id"] = tweet_ref.id
                    tweet["user"] = tweet_user_info

                    tweets_array.append(tweet)

                user_dict["tweets"] = tweets_array
                latest_tweets = user_dict["tweets"]
            else:
                user_dict['tweets'] = []

            if len(logged_in_user_dict.get("following")) > 0:

                following_ref_array = logged_in_user_dict.get("following")

                latest_tweets = await get_last_limited_tweets(following_ref_array, id)

                for following_ref in following_ref_array:
                    if logged_in_user_id and following_ref.id == id:
                        user_dict["is_following"] = True

            return {"user_dict": user_dict, "latest_tweets": latest_tweets}

        else:
            return None
    except Exception as e:
        print(e)
        return None


async def get_single_tweet(id: str):

    tweet_dict = {}

    try:
        tweet_ref = tweets_ref.document(id)
        tweet = tweet_ref.get().to_dict()
        tweet_user_info = tweet["user"].get().to_dict()
        tweet_user_info["user_id"] = tweet["user"].id

        tweet["id"] = tweet_ref.id
        tweet["user"] = tweet_user_info

        tweet_dict = tweet

    except Exception as e:
        print(e)

    return tweet_dict


@TW.post("/set_profile_picture")
async def set_user_profile_picture(
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


@TW.post("/set_cover_picture")
async def set_user_cover_picture(
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

        users_ref.document(user_info["user_id"]).update({"cover_img_url": img_url})

        return JSONResponse(
            content={"msg": "New cover image has been uploaded"}, status_code=200
        )

    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail={"error": "someting went wrong"})


@TW.post("/post")
async def post_tweet(
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
                "date_and_time": firestore.SERVER_TIMESTAMP,
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
async def set_username(req: Request, username: str):

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

        users_ref.document(user_info["user_id"]).set(
            {"username": username, "following": [], "followers": 0}
        )

        return JSONResponse(content={"msg": "username has been set"}, status_code=201)

    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"error": "someting went wrong"})


@TW.get("/follow")
async def on_follow(req: Request, following_user_id: str):
    try:
        user_info = req.state.user_info

        if len(user_info) == 0:
            return RedirectResponse("/login")

        user_id = user_info["user_id"]
        following_user_ref = users_ref.document(following_user_id)
        own_user_ref = users_ref.document(user_id)

        following_user_ref.update(
            {"followers": following_user_ref.get().to_dict().get("followers") + 1}
        )

        own_user_ref.update({"following": firestore.ArrayUnion([following_user_ref])})

        return JSONResponse(status_code=200, content={"msg": "Following on"})

    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"error": "someting went wrong"})


@TW.get("/unfollow")
async def unfollow(req: Request, following_user_id: str):
    try:
        user_info = req.state.user_info

        if len(user_info) == 0:
            return RedirectResponse("/login")

        user_id = user_info["user_id"]
        following_user_ref = users_ref.document(following_user_id)
        own_user_ref = users_ref.document(user_id)

        following_user_ref.update(
            {"followers": following_user_ref.get().to_dict().get("followers") - 1}
        )

        own_user_ref.update({"following": firestore.ArrayRemove([following_user_ref])})

        return JSONResponse(status_code=200, content={"msg": "Following on"})

    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"error": "someting went wrong"})


@TW.post("/edit_tweet")
async def edit_tweet(
    req: Request,
    tweet_id: str,
    tweet: Annotated[str, Form()],
    tweet_type: Annotated[str, Form()],
    file: Annotated[UploadFile | None, File()] = None,
):
    try:
        user_info = req.state.user_info

        if len(user_info) == 0:
            return RedirectResponse("/login")

        tweet_ref = tweets_ref.document(tweet_id)

        if file == None:
            tweet_ref.update({"tweet": tweet, "type": tweet_type})

        if file:

            blob = storage.Blob(name=file.filename, bucket=bucket)
            blob.upload_from_file(file.file)
            img_url = (
                "https://storage.cloud.google.com/"
                + PROJECT_STORAGE_BUCKET
                + "/"
                + file.filename
            )

            tweet_ref.update({"tweet": tweet, "type": tweet_type, "img_url": img_url})

            return JSONResponse(
                content={"msg": "The tweet has been updated"}, status_code=200
            )

    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"error": "someting went wrong"})


@TW.delete("/tweet")
async def delete_tweet(req: Request, tweet_id: str):

    try:
        user_info = req.state.user_info

        if len(user_info) == 0:
            return RedirectResponse("/login")

        tweet_ref = tweets_ref.document(tweet_id)
        user_ref = tweet_ref.get().to_dict().get("user")

        user_ref.update({"tweets": firestore.ArrayRemove([tweet_ref])})
        tweet_ref.delete()

        return JSONResponse(
            content={"msg": "The tweet has been deleted"}, status_code=200
        )

    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"error": "someting went wrong"})
