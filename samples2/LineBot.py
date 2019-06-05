"""
@author:
https://gist.github.com/rifleak74
作者：
楊超霆（臺灣行銷研究有限公司 資料科學研發工程師）
https://medium.com/pythonstock/%E8%82%A1%E7%A5%A8%E5%B0%8F%E7%A7%98%E6%9B%B8%E5%B9%AB%E4%BD%A0%E6%8E%8C%E6%8F%A1-%E5%85%AC%E5%8F%B8%E9%87%8D%E5%A4%A7%E8%A8%8A%E6%81%AF-%E7%AC%AC%E4%B8%80%E6%99%82%E9%96%93%E5%B0%B1%E5%85%88%E8%B7%91-%E9%99%84python%E7%A8%8B%E5%BC%8F%E7%A2%BC-ef9a4c63a2e2
"""

#載入LineBot所需要的套件
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
)

app = Flask(__name__)

# 必須放上自己的Channel Access Token
line_bot_api = LineBotApi('YOUR_CHANNEL_ACCESS_TOKEN')
# 必須放上自己的Channel Secret
handler = WebhookHandler('YOUR_CHANNEL_SECRET')

# 監聽所有來自 /callback 的 Post Request
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

#訊息傳遞區塊
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text=event.message.text)
    line_bot_api.reply_message(event.reply_token,message)

#主程式
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
