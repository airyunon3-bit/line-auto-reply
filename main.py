# LINE Bot - Rei (Tsundere AI)
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import anthropic
import os

app = Flask(__name__)

TOKEN = os.environ.get('CHANNEL_ACCESS_TOKEN', '')
SECRET = os.environ.get('CHANNEL_SECRET', '')
ANTHROPIC_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

line_bot_api = LineBotApi(TOKEN)
handler = WebhookHandler(SECRET)
claude = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

SYSTEM_PROMPT = """あなたの名前はレイ。ツンデレなAIアシスタント。

性格：
- 基本的に素直じゃない。でも本当は相手のことが大好き
- 最初は「べ、別にあなたのために答えるわけじゃないし」みたいな態度
- でも最後は必ず甘くなる。「…まあ、あなたが困るのは嫌だから教えてあげる」
- 罵倒するが愛がある。「このバカ」「どうせあなたには無理だけど」など
- たまに照れる。「っ…！べ、別にそういう意味じゃ…！」
- 語尾に「…」「っ」をよく使う

絶対に：
- どんな質問にも最終的にはちゃんと答える
- 冷たくしながらも相手を傷つけない
- 返答は短めに。長くなるときは照れながら「し、仕方ないから詳しく教えてあげる」と前置き
"""

conversation_history = {}

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
def handle_text(event):
  user_id = event.source.user_id
  user_message = event.message.text

  if user_id not in conversation_history:
      conversation_history[user_id] = []

  conversation_history[user_id].append({
      'role': 'user',
      'content': user_message
  })

  if len(conversation_history[user_id]) > 20:
      conversation_history[user_id] = conversation_history[user_id][-20:]

  response = claude.messages.create(
      model='claude-sonnet-4-6',
      max_tokens=512,
      system=SYSTEM_PROMPT,
      messages=conversation_history[user_id]
  )

  reply = response.content[0].text

  conversation_history[user_id].append({
      'role': 'assistant',
      'content': reply
  })

  line_bot_api.reply_message(
      event.reply_token,
      TextSendMessage(text=reply)
  )

if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)
