from google.cloud import firestore, storage
from google.oauth2 import service_account


PROJECT_NAME = "twitter-63278"
PROJECT_STORAGE_BUCKET = "twitter-63278.appspot.com"


credentials = service_account.Credentials.from_service_account_file(
    "config/twitter-63278-firebase-adminsdk-h7anp-b21d0a3f4c.json"
)

db = firestore.Client(credentials=credentials)

client_storage = storage.Client(project=PROJECT_STORAGE_BUCKET, credentials=credentials)
bucket = client_storage.bucket(bucket_name=PROJECT_STORAGE_BUCKET)
