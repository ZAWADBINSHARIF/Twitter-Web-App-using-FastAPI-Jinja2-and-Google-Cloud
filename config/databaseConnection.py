from google.cloud import firestore
from google.oauth2 import service_account


credentials = service_account.Credentials.from_service_account_file(
    "config/twitter-63278-firebase-adminsdk-h7anp-b21d0a3f4c.json"
)

db = firestore.Client(credentials=credentials)
