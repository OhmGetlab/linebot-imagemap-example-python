# -*- coding: utf-8 -*-
import sys
sys.path.append('./vendor')

import os
import uuid

from PIL import Image
import io

from flask import Flask, request, abort, send_file

from linebot import (
    LineBotApi, WebhookHandler,
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, MessageImagemapAction, ImagemapArea, ImagemapSendMessage, BaseSize
)

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('CHANNEL_SECRET'))

@app.route("/", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.type == "message":
        if event.message.type == "text":
            actions = []
            actions.append(MessageImagemapAction(
                text = 'Button Pushed!',
                area = ImagemapArea(
                    # Button is 100px on 700px. So 149 on base size(1040px)
                    x = 0, y = 0, width = 149, height = 149
                )
            ))
            message = ImagemapSendMessage(
                base_url = 'https://' + request.host + '/imagemap/' + uuid.uuid4().hex, # prevent cache
                alt_text = '代替テキスト',
                base_size = BaseSize(height=1040, width=1040),
                actions = actions
            )
            line_bot_api.reply_message(event.reply_token, message)

@app.route("/imagemap/<uniqid>/<size>", methods=['GET'])
def imagemap(uniqid, size):
    img = Image.open("./imagemap.png")
    img_resize = img.resize((int(size), int(size)))
    img_io = io.BytesIO()
    img_resize.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

if __name__ == "__main__":
    app.debug = True
    app.run()
