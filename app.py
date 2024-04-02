import inspect

# inspectモジュールにgetargspec属性がない場合、getfullargspecを使用する
if not hasattr(inspect, 'getargspec'):
    inspect.getargspec = inspect.getfullargspec

# その他のimport文
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
import random

app = Flask(__name__)

# LINE Developersのチャネルシークレットとチャネルアクセストークンを設定
CHANNEL_ACCESS_TOKEN = '712FYpF+e+43jXB7sBk/Mye6mgFY5hC/GP6GmbfCbGUj9o9UDkhdJjzZZErayY51XUT08uvcdjeU1U/T+nuJPFIJedhOp2bXRof0QFz1hupcj62X9FddD7F8FhY4tf6/LrjMh5co5+39MDaV1UiYJgdB04t89/1O/w1cDnyilFU='
CHANNEL_SECRET = 'ee06db0d98cefc68a195b906cdbe12d5'

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# ステップごとのメッセージを定義
steps = {
    1: "絵を見ていかがですか？感想を教えてください",
    2: "あなたはどんなタイトルをつけますか？",
    3: "この絵は『雨、蒸気、速度――グレート・ウェスタン鉄道』というタイトルです..."
       "でも，なんだかボヤッとしていますよね．この技法って何というかご存知ですか？\n1 印象派\n2 ぼかし法\n3 古典派",
    4: "印象派の作品には、典型的には、明るい色調、薄く塗られた絵の具、そして独特の筆触が見られます。"
       " これらは、画家たちが目の前に広がるシーンをいかに感じ、そしてその感覚をどのようにキャンバス上に瞬時に表現したかを示しています。\n"
       "そのままですね．あなたは印象派の絵を描くとしたらどんな絵を描きたいと思いますか？",
    5: "この絵の作者，ターナーは光と色彩で自然を表現しようとしたイギリスの画家です．1844年に描かれました．"
       "グレート・ウェスタン鉄道は、ロンドンと南西・西部イングランドおよびウェールズの大半を結んでいた、かつてのイギリスの鉄道会社です．"
       "この絵はある大物アーティストが歌にしています．さて誰でしょう？\n1　サザンオールスターズ\n2　チェッカーズ\n3　山下達郎",
    6: "正解は山下達郎で，ターナーの機関車という曲を書いています．是非聞いてみてくださいね．学習お疲れ様でした．感想や質問はありますか？"
}

# 正解の回答
correct_answers = {3: "1", 5: "3"}

current_step = 0

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    handler.handle(body, signature)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global current_step
    user_message = event.message.text
    
    if current_step == 0 and user_message.lower() == "yes":
        current_step = 1
        send_step_message(event)
    else:
        handle_step(user_message, event, inspect.signature(handle_step).parameters)

def handle_step(user_message, event, params):
    global current_step
    if current_step == 0:
        return
    elif current_step == 1:
        current_step = 2
        send_step_message(event)
    elif current_step == 2:
        current_step = 3
        send_step_message(event)
    elif current_step == 3:
        if user_message != correct_answers.get(3):
            send_retry_message(event)
        else:
            current_step = 4
            send_step_message(event)
    elif current_step == 4:
        current_step = 5
        send_step_message(event)
    elif current_step == 5:
        if user_message != correct_answers.get(5):
            send_retry_message(event)
        else:
            current_step = 6
            send_step_message(event)
    elif current_step == 6:
        current_step = 0
        send_step_message(event)

def send_step_message(event):
    global current_step
    step_message = steps[current_step]
    if current_step == 1:
        image_message = ImageSendMessage(
            original_content_url='https://ontomo-mag.com/uploads/main_rainsteamandspeed.jpg',
            preview_image_url='https://ontomo-mag.com/uploads/main_rainsteamandspeed.jpg'
        )
        line_bot_api.reply_message(
            event.reply_token,
            [TextSendMessage(text=step_message), image_message]
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=step_message)
        )

def send_retry_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="不正解です。もう一度チャレンジしてください。")
    )

if __name__ == "__main__":
    app.run(port=5001)
