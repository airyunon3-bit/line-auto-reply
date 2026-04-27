# LINE Auto Reply Bot
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

app = Flask(__name__)

TOKEN = os.environ.get('CHANNEL_ACCESS_TOKEN', '')
SECRET = os.environ.get('CHANNEL_SECRET', '')

print(f"TOKEN exists: {bool(TOKEN)}")
print(f"SECRET exists: {bool(SECRET)}")

line_bot_api = LineBotApi(TOKEN)
handler = WebhookHandler(SECRET)

KEYWORDS = {
    '参加': 'サロンへの参加はこちらからどうぞ → https://example.com/join',
    '料金': '月額料金は3,980円です。初月無料キャンペーン中！',
    '特典': '特典：限定動画 / 週1ライブQ&A / 専用コミュニティ',
    'LINE': 'LINE運用のコツ → 詳細はこちら https://example.com/tips',
}

@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    reply = None
    for keyword, response in KEYWORDS.items():
        if keyword in text:
            reply = response
            break
    if reply:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
