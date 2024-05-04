# external import
from fastapi import UploadFile
from pydantic import BaseModel


class PostTweet(BaseModel):
    tweet: str
    type: str
