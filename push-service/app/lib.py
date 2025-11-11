import asyncio
import httpx
from pyfcm import FCMNotification
from google.oauth2 import credentials
from dotenv import load_dotenv
import os
import json
from main import logger

load_dotenv()

TEMPLATE_URL = os.getenv('TEMPLATE_URL')
GOOGLE_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

if not TEMPLATE_URL:
    raise Exception('Template microservice url not provided')

if not GOOGLE_CREDENTIALS:
    raise Exception('Google application credential not provided')

GOOGLE_CREDENTIALS = json.loads(GOOGLE_CREDENTIALS)

# exponential backoff helper
async def sleep_backoff(attempt: int):
    await asyncio.sleep(min(60, (2 ** attempt)))

async def fetch_rendered_template(code: str, variable: dict) -> str:
    logger.info(f"fetched rendered template {code} variables: {json.dumps(variable)}")
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(f'{TEMPLATE_URL}/render/{code}')
        r.raise_for_status()
        return r.json().get('rendered')
    
async def send_fcm(token: str, title: str, body: str, data: dict | None = None):
    logger.info(f"Attempted to send message with details {title} {body} {json.dumps(data)} {token}")
    push_service = FCMNotification(credentials=credentials.Credentials(GOOGLE_CREDENTIALS))
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, lambda: push_service.notify(fcm_token=token ,notification_body=body, notification_title=title, data_payload=data or {}))
    return result

