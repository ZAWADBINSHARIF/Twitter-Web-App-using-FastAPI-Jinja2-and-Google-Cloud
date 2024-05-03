# external import
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.exceptions import HTTPException
from datetime import datetime


# internal import
from config.databaseConnection import db, firestore


users_ref = db.collection("users")


TW = databaseRoutes = APIRouter(prefix="/tw")


async def get_user_info(id: str):

    user = users_ref.document(id).get()

    return user


@TW.post("/post")
async def get_user(req: Request, username: str):
    print(username)
    try:
        user_info = req.state.user_info

        if len(user_info) == 0:
            return RedirectResponse("/login")

        user_ref = users_ref.document(user_info["user_id"])

        return JSONResponse(content={"msg": "username has been set"}, status_code=201)

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
