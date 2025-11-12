from datetime import datetime, timezone
from fastapi import FastAPI
import aio_pika
import os
import json
from redis import asyncio as aioredis
from lib import sleep_backoff, send_fcm, fetch_rendered_template
from dotenv import load_dotenv
import sys

from model import PushMessage
import logging

load_dotenv()


logger = logging.getLogger('fastapi_app')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler('fastapi.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(stdout_handler)


RABBIT_URL = os.getenv('RABBITMQ_URL')

TEMPLATE_SERVICE_URL = os.getenv('TEMPLATE_SERVICE_URL')

REDIS_URL = os.getenv('REDIS_URL')

if not TEMPLATE_SERVICE_URL:
    raise Exception('Template service url not found')

if not REDIS_URL:
    raise Exception('Redis URL not Set')

if not RABBIT_URL:
    raise Exception('Rabbit service url not provided')

app = FastAPI(title='Push Service')


@app.on_event('startup')
async def startup():
    app.state.redis = await aioredis.from_url(REDIS_URL)
    app.state.rabbit_conn = await aio_pika.connect_robust(RABBIT_URL)
    app.state.channel = await app.state.rabbit_conn.channel()
    await app.state.channel.set_qos(prefetch_count=10)
    queue = await app.state.channel.declare_queue('push.queue', durable=True)
    await queue.consume(on_message)


@app.on_event('shutdown')
async def shutdown():
    await app.state.rabbit_conn.close()
    await app.state.redis.close()


@app.get('/health')
async def health():
    logger.info('Health point accessed')
    return {"status": "ok"}


@app.post('/send/')
async def send_push(payload: PushMessage):
    # For quick testing: publish to rabbitmq
    logger.info(f"Raw json payload: {json.dumps(payload, indent=2)}")

    conn = await aio_pika.connect_robust(RABBIT_URL)
    channel = await conn.channel()
    await channel.default_exchange.publish(
        aio_pika.Message(body=json.dumps(payload.dict()).encode(), delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
        routing_key='push.queue'
    )
    await conn.close()
    return {"success": True, "message": "queued"}

# Idempotency key helper
async def is_processed(request_id: str) -> bool:
    logging.info(f"Checked if {request_id} was processed")
    return await app.state.redis.get(f"processed:{request_id}") is not None

async def mark_processed(request_id: str, ttl: int = 60*60*24):
    logging.info(f"marked {request_id} as processed")
    await app.state.redis.set(f"processed:{request_id}", "1", ex=ttl)

async def on_message(message: aio_pika.abc.AbstractIncomingMessage):
    logging.info(f"called on_message on {json.dumps(message)}")
    async with message.process(requeue=False):
        try:
            payload = json.loads(message.body)
            request_id = payload.get('request_id')
            # idempotency check
            if await is_processed(request_id):
                return

            # fetch user push token and preferences - in production call User Service; here assume payload includes push_token
            token = payload.get('metadata', {}).get('push_token')
            if not token:
                # could call user service here; skip
                print('no token')
                return

            # render template
            attempt = 0
            max_attempts = 5
            while attempt < max_attempts:
                try:
                    rendered = await fetch_rendered_template(payload['template_code'], payload.get('variables', {}))
                    break
                except Exception as e:
                    attempt += 1
                    await sleep_backoff(attempt)
            else:
                # move to dead-letter queue
                await app.state.channel.default_exchange.publish(
                    aio_pika.Message(body=message.body, delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
                    routing_key='failed.queue'
                )
                return

            # send via FCM
            attempt = 0
            while attempt < max_attempts:
                try:
                    # simple payload: assume rendered contains title and body split by newline, or entire body
                    title = payload.get('metadata', {}).get('title') or 'Notification'
                    body_text = rendered
                    resp = await send_fcm(token, title, body_text, data=payload.get('metadata'))
                    # check response for failure
                    if resp.get('failure'):
                        raise Exception('fcm failure')
                    # mark processed
                    await mark_processed(request_id)
                    # publish status update (synchronous/async pattern)
                    await app.state.channel.default_exchange.publish(
                        aio_pika.Message(body=json.dumps({
                            'notification_id': request_id,
                            'status': 'delivered',
                            'timestamp': datetime.now(timezone.utc)
                        }).encode(), delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
                        routing_key='notification.status'
                    )
                    break
                except Exception as e:
                    attempt += 1
                    await sleep_backoff(attempt)
            else:
                # permanent failure
                await app.state.channel.default_exchange.publish(
                    aio_pika.Message(body=message.body, delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
                    routing_key='failed.queue'
                )
                # publish failed status
                await app.state.channel.default_exchange.publish(
                    aio_pika.Message(body=json.dumps({
                        'notification_id': request_id,
                        'status': 'failed',
                        'timestamp': datetime.now(timezone.utc),
                        'error': 'fcm send failed'
                    }).encode(), delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
                    routing_key='notification.status'
                )
        except Exception as exc:
            # ensure message doesn't get lost — move to failed queue
            await app.state.channel.default_exchange.publish(
                aio_pika.Message(body=message.body, delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
                routing_key='failed.queue'
            )
            print('error processing message', exc)


@app.post('/{notification_reference}/status')
async def notification_status(notification_reference: str):
    ...