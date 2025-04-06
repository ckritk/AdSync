import os
import mimetypes
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate_drive():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def upload_to_drive(file_path):
    creds = authenticate_drive()
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {'name': os.path.basename(file_path)}
    media = MediaFileUpload(file_path, resumable=True, mimetype=mimetypes.guess_type(file_path)[0])

    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    # Make it shareable
    service.permissions().create(fileId=file['id'], body={'type': 'anyone', 'role': 'reader'}).execute()

    file_id = file.get('id')
    return f"https://drive.google.com/uc?export=download&id={file_id}"
