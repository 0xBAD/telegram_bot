import config
import requests


def send_message(chat_id, text, parse_mode="Markdown"):
    url_send = config.api_url + config.token + "/sendMessage"
    data = dict(chat_id=chat_id, text=text, parse_mode=parse_mode)
    return requests.post(url_send, data)
