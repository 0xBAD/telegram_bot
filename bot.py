#!/usr/bin/python3.5
# -*- coding: utf-8 -*-
import signal
from time import time, asctime

import requests
import tornado.escape
import tornado.ioloop
import tornado.web
from tornado.options import parse_command_line

import config
from classes.user import DBStat, User, Message
from lib.api import sendMessage


status_messages = {200: 'Status 200. Ok',
                   404: 'Not Found',
                   500: 'Status 500. Internal server error'
                   }

# Список доступных комманд
available_commands = ['/start', '/help ', '/ping ',  ]



def send_welcome(chat_id):
    sendMessage(chat_id, "Привет! Я бот!\nЧтобы узнать что я умею отправь мне /help")


def help_message(chat_id):
    text = "Вот команды которые мне доступны:\n"
    for command in available_commands:
        text += (command + " \n")
    sendMessage(chat_id=chat_id, text=text, parse_mode=None)


def repeat_all_messages(message):
    sendMessage(message['chat']['id'], message['text'][6:])


def ping():
    url = "https://google.com/"
    response = requests.head(url)
    return response


def getChat(chat_id):
    url_send = config.api_url + config.token + "/getChat"
    data = dict(chat_id=chat_id)
    print(data)
    return requests.post(url_send,data)


def signal_term_handler(signum, frame):
    print ('Signal handler called with signal')
    exit(1)


def main():
    parse_command_line()
    signal.signal(signal.SIGTERM, signal_term_handler)
    try:
        cert_file = open(config.cert_path,'rb')
        bot_url = config.MyURL
        set_hook = requests.post(config.api_url + config.token + "/setWebhook",
                                 data=dict(url=bot_url),
                                 files=dict(certificate=cert_file))
        if set_hook.status_code != 200:
            log("Can't set hook: %s. Quit." % set_hook.text)
            exit(1)
        print("Bot started")
        app = tornado.web.Application(
            [
                (r'/hook', MainHandler),
            ],
            cookie_secret="pm3MXxAXIfzmSPSUW8b3vI", #random_string
            xsrf_cookies=False,
            debug=True,
        )
        app.listen(config.PORT_NUMBER)
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        signal_term_handler(signal.SIGTERM, None)


# сообщение в личку админу
def log(text):
    sendMessage(chat_id=config.ADMIN_ID,text=text)


# хэндлер
class MainHandler(tornado.web.RequestHandler):
    def check_xsrf_cookie(self):
        pass

    def post(self):

        try:
            data = tornado.escape.json_decode(self.request.body)
            print(data)

            if 'text' not in data['message']:
                return
            db = DBStat()
            if not db.check_user(data['message']['from']['id']):
                user_data = data['message'].get('from')
                user = User(user_id=user_data.get('id'),
                            first_name=user_data.get('first_name'),
                            last_name=user_data.get('last_name'),
                            username=user_data.get('username'),
                            language_code=user_data.get('language_code'))
                db.add_new_user(user)
            chat_id = data['message']['chat']['id']
            command = data['message']['text']

            # Если начинается с / значит это команда и надо залогировать
            if command[:1] == '/':
                message = Message(message_id=data['message']['message_id'], text=command, chat_id=chat_id,
                                  date=time(), from_id=data['message'].get('from').get('id'))
                db.add_new_message(message)

            if command[:6] == '/start':
                send_welcome(chat_id)
            elif command[:5] == '/help':
                help_message(chat_id)
            elif command[:5] == '/test':
                repeat_all_messages(data['message'])
            elif command[:5] == '/ping':
                response = ping()
                if response.status_code in status_messages:
                    text = status_messages[response.status_code]
                else:
                    text = response
                sendMessage(chat_id, text)



        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            log(tb)

if __name__ == '__main__':
    main()
