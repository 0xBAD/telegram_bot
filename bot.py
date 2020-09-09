#!/usr/bin/python3.7

import signal
from abc import ABC
from time import time

import requests
import tornado.escape
import tornado.ioloop
import tornado.web
from tornado.options import parse_command_line

import config
from classes.user import DBStat, User, Message
from classes.logger import log
from lib.api import send_message

COOKIE_SECRET_WORD = "HJFDHJFHDJHJH"
status_messages = {200: 'Status 200. Ok',
                   404: 'Not Found',
                   500: 'Status 500. Internal server error'
                   }

available_commands = ['/start', '/help ', '/ping ', ]


def send_welcome(chat_id):
    send_message(chat_id, "Hi, meat bag!\nIf you wanna know list of my commands send me /help")


def help_message(chat_id):
    text = "There are available commands:\n"
    for command in available_commands:
        text += (command + " \n")
    send_message(chat_id=chat_id, text=text, parse_mode=None)


def repeat_all_messages(message):
    send_message(message['chat']['id'], message['text'][6:])


def ping():
    url = "https://google.com/"
    response = requests.head(url)
    return response


def get_chat(chat_id):
    url_send = config.api_url + config.token + "/getChat"
    data = dict(chat_id=chat_id)
    send_to_admin(data)
    return requests.post(url_send, data)


def signal_term_handler(signum, frame):
    log.info(f"Signal handler called with signal {signum} - {frame}")
    exit(1)


def main():
    parse_command_line()
    signal.signal(signal.SIGTERM, signal_term_handler)
    try:
        cert_file = open(config.cert_path, 'rb')
        bot_url = config.MyURL
        set_hook = requests.post(config.api_url + config.token + "/setWebhook",
                                 data=dict(url=bot_url),
                                 files=dict(certificate=cert_file))
        if set_hook.status_code != 200:
            msg = f"Can't set hook: {set_hook.text}. Quit."
            raise Exception(msg)
        log.info("Bot started")
        app = tornado.web.Application(
            [
                (r'/hook', MainHandler),
            ],
            cookie_secret=COOKIE_SECRET_WORD,
            xsrf_cookies=False,
            debug=True,
        )
        app.listen(config.PORT_NUMBER)
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        signal_term_handler(signal.SIGTERM, None)
    except Exception as e:
        log.error(e)


def send_to_admin(text):
    """
    sends message to admin
    :param text:
    :return:
    """
    send_message(chat_id=config.ADMIN_ID, text=text)


class MainHandler(tornado.web.RequestHandler, ABC):
    def check_xsrf_cookie(self):
        pass

    def post(self):

        try:
            data = tornado.escape.json_decode(self.request.body)
            log.info(data)

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

            if command[0] == '/':
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
                send_message(chat_id, text)
        except Exception as e:
            log.error(e)


if __name__ == '__main__':
    main()
