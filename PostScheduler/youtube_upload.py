import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_authenticated_service():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build('youtube', 'v3', credentials=creds)

def upload_video(video_path, title, description="Uploaded via API", tags=["shorts"], categoryId="22", privacyStatus="public"):
    youtube = get_authenticated_service()
    request_body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': categoryId,
        },
        'status': {
            'privacyStatus': privacyStatus,
            'selfDeclaredMadeForKids': False
        }
    }

    media = MediaFileUpload(video_path, mimetype='video/*', resumable=True)
    response_upload = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    ).execute()

    print("📺 YouTube Upload Successful:", response_upload.get("id"))
    return response_upload.get("id")
