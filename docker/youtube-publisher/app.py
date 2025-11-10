from flask import Flask, jsonify, request, redirect, url_for
import os, json, pathlib, logging, time
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# Optional Secret Manager integration
try:
    from google.cloud import secretmanager
    HAS_SECRET_MANAGER = True
except Exception:
    HAS_SECRET_MANAGER = False

app = Flask(__name__)
CRED_DIR = pathlib.Path('/app/credentials')
CRED_DIR.mkdir(parents=True, exist_ok=True)
CLIENT_SECRETS = '/app/config/secrets.yaml'

def load_client_secrets():
    import yaml
    p = pathlib.Path(CLIENT_SECRETS)
    if not p.exists():
        return None
    data = yaml.safe_load(p.read_text())
    return data.get('youtube', {})

def save_credentials_locally(creds):
    cred_path = CRED_DIR / 'credentials.json'
    cred_path.write_text(json.dumps({
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes,
        'expiry': creds.expiry.isoformat() if creds.expiry else None
    }))
    return str(cred_path)

def load_credentials_locally():
    cred_path = CRED_DIR / 'credentials.json'
    if not cred_path.exists():
        return None
    data = json.loads(cred_path.read_text())
    creds = Credentials(
        token=data.get('token'),
        refresh_token=data.get('refresh_token'),
        token_uri=data.get('token_uri'),
        client_id=data.get('client_id'),
        client_secret=data.get('client_secret'),
        scopes=data.get('scopes')
    )
    return creds

def save_credentials_to_secret_manager(secret_id, creds):
    if not HAS_SECRET_MANAGER:
        raise RuntimeError('google-cloud-secret-manager not installed or unavailable')
    client = secretmanager.SecretManagerServiceClient()
    parent = f"projects/{os.environ.get('GCP_PROJECT_ID')}"
    # Create secret if it doesn't exist (idempotent naive attempt)
    try:
        client.create_secret(request={
            "parent": parent,
            "secret_id": secret_id,
            "secret": {"replication": {"automatic": {}}}
        })
    except Exception:
        pass
    payload = json.dumps({
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }).encode('UTF-8')
    name = f"projects/{os.environ.get('GCP_PROJECT_ID')}/secrets/{secret_id}/versions"
    client.add_secret_version(request={"parent": name, "payload": {"data": payload}})
    return True

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/auth')
def auth():
    secrets = load_client_secrets()
    if not secrets or not secrets.get('client_id') or not secrets.get('client_secret'):
        return jsonify({'error': 'Missing client_id / client_secret in config/secrets.yaml'}), 400
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": secrets['client_id'],
                "client_secret": secrets['client_secret'],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [secrets.get('redirect_uri', 'http://localhost:8030/oauth2callback')]
            }
        },
        scopes=["https://www.googleapis.com/auth/youtube.upload", "openid", "https://www.googleapis.com/auth/userinfo.email"]
    )
    flow.redirect_uri = secrets.get('redirect_uri', 'http://localhost:8030/oauth2callback')
    auth_url, _ = flow.authorization_url(prompt='consent', include_granted_scopes='true', access_type='offline')
    return redirect(auth_url)

@app.route('/oauth2callback')
def oauth2callback():
    secrets = load_client_secrets()
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": secrets['client_id'],
                "client_secret": secrets['client_secret'],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [secrets.get('redirect_uri', 'http://localhost:8030/oauth2callback')]
            }
        },
        scopes=["https://www.googleapis.com/auth/youtube.upload", "openid", "https://www.googleapis.com/auth/userinfo.email"]
    )
    flow.redirect_uri = secrets.get('redirect_uri', 'http://localhost:8030/oauth2callback')
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    creds = flow.credentials
    save_credentials_locally(creds)
    # Optionally save to Secret Manager if configured
    sm_id = os.environ.get('YOUTUBE_SM_SECRET_ID')
    if sm_id and HAS_SECRET_MANAGER and os.environ.get('GCP_PROJECT_ID'):
        try:
            save_credentials_to_secret_manager(sm_id, creds)
        except Exception as e:
            logging.exception('Failed to save to Secret Manager: %s', e)
    return jsonify({'status': 'credentials_saved'})

def refresh_credentials(creds):
    if not creds or not creds.refresh_token:
        return creds
    request_adapter = Request()
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(request_adapter)
        except Exception as e:
            logging.exception('Failed to refresh token: %s', e)
    return creds

@app.route('/publish', methods=['POST'])
def publish():
    body = request.json or {}
    # load credentials - prefer Secret Manager when configured
    creds = None
    sm_id = os.environ.get('YOUTUBE_SM_SECRET_ID')
    if sm_id and HAS_SECRET_MANAGER and os.environ.get('GCP_PROJECT_ID'):
        try:
            client = secretmanager.SecretManagerServiceClient()
            name = f"projects/{os.environ.get('GCP_PROJECT_ID')}/secrets/{sm_id}/versions/latest"
            response = client.access_secret_version(request={"name": name})
            data = json.loads(response.payload.data.decode('utf-8'))
            creds = Credentials(
                token=data.get('token'),
                refresh_token=data.get('refresh_token'),
                token_uri=data.get('token_uri'),
                client_id=data.get('client_id'),
                client_secret=data.get('client_secret'),
                scopes=data.get('scopes')
            )
        except Exception as e:
            logging.exception('Secret Manager load failed: %s', e)
    if not creds:
        creds = load_credentials_locally()
    if not creds:
        return jsonify({'error': 'No credentials available. Call /auth and complete OAuth flow.'}), 400

    creds = refresh_credentials(creds)
    # save refreshed credentials locally
    save_credentials_locally(creds)
    # optionally overwrite secret manager
    if sm_id and HAS_SECRET_MANAGER and os.environ.get('GCP_PROJECT_ID'):
        try:
            save_credentials_to_secret_manager(sm_id, creds)
        except Exception as e:
            logging.exception('Failed to save refreshed creds to Secret Manager: %s', e)
    # Build youtube client (simulate upload)
    try:
        youtube = build('youtube', 'v3', credentials=creds)
        # Real upload flow would use youtube.videos().insert with media_body
        return jsonify({'status': 'ready_to_upload', 'metadata': body})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
