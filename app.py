import json
import requests
import os
import time

import errno
import sys
import tempfile
import random
from argparse import ArgumentParser
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageTemplateAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URITemplateAction,
    PostbackTemplateAction, DatetimePickerTemplateAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent
)

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
# change channel_secret and channel_access_token from your line developer
channel_secret = os.getenv('LINE_CHANNEL_SECRET', "15187f12f95fce8324cc3a408c169a87")
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', "lj13Y4NZCR6PqlpEewh0R/rs9NR5RMIsytAA7ElmybG1P4daMFC+0h+jXBWwXpJrYXCaMp8OOSH2IR9CbpNRjrg/Sg8h8TPLaqHElM3N8/cK8PBUgLegHI3G7cuEgclmgDVpLhNSR/mZ1nIVMSupPQdB04t89/1O/w1cDnyilFU=")
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

# change this variable with your server API 
api_url = "http://35.229.124.57"
api_port = ":5000"
api_route = "/predict"

@app.route("/test", methods=['GET'])
def test():
    sys.stdout.write("test request received\n")
    return "test"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# Nanti fungsi request_api ini diletakkan seperti ini:
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    question = event.message.text
    answer = request_api(question)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=answer))

def request_api(question):
    url = api_url + api_port + api_route
    payload = {"question": question}

    response_data = ""
    while response_data == "":
        try:
            print "ISSUING POST REQUEST..."
            session = requests.Session()
            req = session.post(url, data=payload, timeout=15)
            response_data = str(req.text)
        except:
            print "Connection timeout..."
            print "Retrying post request..."
            time.Sleep(1)
            continue
    
    response_data = json.JSONDecoder().decode(response_data)
    return response_data["answer"]

if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=5000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    # create tmp dir for download content
    make_static_tmp_dir()

    app.run(debug=options.debug, port=options.port)

