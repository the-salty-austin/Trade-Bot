# encoding: utf-8
from getBinanceData import calculate_ta
import pandas as pd

from flask import Flask, request, abort

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError,
    LineBotApiError
)
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    TemplateSendMessage,
    ButtonsTemplate,
    MessageTemplateAction,
    PostbackEvent,
    PostbackTemplateAction
)

app = Flask(__name__)

# you can replace by load env file
handler = WebhookHandler('e6e8b8917989a634ae78671aaf1d461a')
line_bot_api = LineBotApi('nuKoyvdheU7WW9KaWGsNSgOsroOYQa0lIGz0xjbn9s77wY5OjB/9hWciv9LTxdWf5KDqpf99BDMxLISGEJv8MUz/Qjq/voxQWyajTLjbxfkgTBh8xQ48nh/CFCRpewRSo21gwfnjxODkprGfLLqDBAdB04t89/1O/w1cDnyilFU=') 

# line_bot_api.push_message('U37d002cad8c0e5ad30670cd47940a1bb', TextSendMessage(text='Bot initiated...'))

@app.route('/')
def index():
    return "<p>Hello World!</p>"

# @csrf_exempt
@app.route("/callback", methods=['POST'])
def callback():

    if request.method == 'POST':
        signature = request.headers['X-Line-Signature']
        body = request.get_data(as_text=True)

        try:
            events = handler.handle(body, signature)  # 傳入的事件
        except InvalidSignatureError:
            print('Invalid Signature')
            return HttpResponseForbidden()
        except LineBotApiError:
            print('LineBot API error')
            return HttpResponseBadRequest()

        # for event in events:
        #     if isinstance(event, MessageEvent):  # 如果有訊息事件
        #         if event.message.text == "哈囉":
        #             select_symbol(event)

        #     elif isinstance(event, PostbackEvent):
        #         if event.postback.data[0:1] == 'S':
            
        #             symbol = event.postback.data[2:]
        #             select_analyze_mode(event, symbol)

        #         elif event.postback.data[0:1] == "T":
                    
        #             ta_request = event.postback.data[2:].split('&')
        #             symbol = ta_request[0]
        #             ta_indicator = ta_request[1]
        #             event.reply_token,
        #             TextSendMessage(text=f'''
        #             https://www.binance.com/zh-TW/trade/{symbol[:-4]}_USDT\n
        #             Technical Indicator ({ta_indicator}) not avialable now :(''')
        # return HttpResponse()
    else:
        return HttpResponseBadRequest()
    
    # # get X-Line-Signature header value
    # signature = request.headers['X-Line-Signature']

    # # get request body as text
    # body = request.get_data(as_text=True)
    # app.logger.info("Request body: " + body)

    # # handle webhook body
    # try:
    #     handler.handle(body, signature)
    # except InvalidSignatureError:
    #     abort(400)

    return 'OK'

# ========== handle user message ==========
@handler.add(MessageEvent, message=TextMessage)  
def handle_text_message(event):
    # message from user                  
    msg = event.message.text

    print(msg)
    
    if msg == 'Hello':
        event = select_symbol(event)
    
    elif msg[0:1] == 'S':
        
        symbol = msg[2:]
        select_analyze_mode(event, symbol)

    elif msg[0:1] == "T":
        
        ta_request = msg[2:].split('&')
        symbol = ta_request[0]
        ta_indicator = ta_request[1]

        df = calculate_ta(symbol)
        if ta_indicator == 'RSI':
            day = str(df['timestamp'].iloc[-1])[:10]
            r06 = df['RSI_06'].iloc[-1]
            r12 = df['RSI_12'].iloc[-1]
            r24 = df['RSI_24'].iloc[-1]


            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=
                f'''[Current Price]
                https://www.binance.com/zh-TW/trade/{symbol[:-4]}_USDT\n
                \n
                [Technical Indicator ({ta_indicator})]\n
                {day}: (6,12,24)=({int(r06)},{int(r12)},{int(r24)})
                ''')
            )
        
        elif ta_indicator == 'KD':
            day = str(df['timestamp'].iloc[-1])[:10]
            k = df['K%'].iloc[-1]
            d = df['D%'].iloc[-1]


            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=
                f'''[Current Price]
                https://www.binance.com/zh-TW/trade/{symbol[:-4]}_USDT\n
                \n
                [Technical Indicator ({ta_indicator})]\n
                {day}: K={int(k)} D={int(d)}
                ''')
            )


def select_symbol(event):
    line_bot_api.reply_message(  # 回復傳入的訊息文字
        event.reply_token,
        TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(
                title='To the moon or CRASH?',
                text='Crypto Symbol',
                actions=[
                    PostbackTemplateAction(
                        label='BTCUSDT',
                        text='S&BTCUSDT',
                        data='S&BTCUSDT'
                    ),
                    PostbackTemplateAction(
                        label='ETHUSDT',
                        text='S&ETHUSDT',
                        data='S&ETHUSDT'
                    ),
                    PostbackTemplateAction(
                        label='DOGEUSDT',
                        text='S&DOGEUSDT',
                        data='S&DOGEUSDT'
                    )
                ]
            )
        )
    )
    return event

def select_analyze_mode(event, symbol):
    line_bot_api.reply_message(   # 回復「選擇美食類別」按鈕樣板訊息
        event.reply_token,
        TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(
                title='Analytical Mode',
                text='Select Technical Index',
                actions=[
                    PostbackTemplateAction(  # 將第一步驟選擇的地區，包含在第二步驟的資料中
                        label='KD',
                        text='T&' + symbol + '&KD',
                        data='T&' + symbol + '&KD'
                    ),
                    PostbackTemplateAction(
                        label='RSI',
                        text='T&' + symbol + '&RSI',
                        data='T&' + symbol + '&RSI'
                    )
                ]
            )
        )
    )

import os
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
