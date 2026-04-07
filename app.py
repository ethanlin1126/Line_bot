import os
import random
import json
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    ImageMessage,
    QuickReply,
    QuickReplyItem,
    MessageAction,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from dotenv import load_dotenv

from handlers.mood import handle_mood
from handlers.commands import handle_command
from handlers.food import handle_food
from handlers.diary import handle_diary
from scheduler import start_scheduler

load_dotenv()

app = Flask(__name__)

configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
with open(os.path.join(DATA_DIR, 'responses.json'), 'r', encoding='utf-8') as f:
    RESPONSES = json.load(f)


def reply(reply_token: str, response):
    if isinstance(response, dict) and response.get('type') == 'memory':
        messages = [
            ImageMessage(
                type='image',
                original_content_url=response['image_url'],
                preview_image_url=response['image_url'],
            ),
            TextMessage(type='text', text=response['text']),
        ]
    elif isinstance(response, dict) and response.get('type') == 'quick_reply':
        messages = [
            TextMessage(
                type='text',
                text=response['text'],
                quick_reply=QuickReply(items=[
                    QuickReplyItem(action=MessageAction(label=opt, text=opt))
                    for opt in response['options']
                ]),
            )
        ]
    else:
        messages = [TextMessage(type='text', text=response)]

    with ApiClient(configuration) as api_client:
        MessagingApi(api_client).reply_message(
            ReplyMessageRequest(reply_token=reply_token, messages=messages)
        )


@app.route('/ping', methods=['GET'])
def ping():
    return 'pong', 200


@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event: MessageEvent):
    text = event.message.text
    user_id = event.source.user_id

    response = (
        handle_food(text, user_id)
        or handle_diary(text, user_id)
        or handle_command(text)
        or handle_mood(text)
        or random.choice(RESPONSES['default'])
    )

    reply(event.reply_token, response)


if __name__ == '__main__':
    start_scheduler()
    app.run(host='0.0.0.0', port=8080, debug=False)
