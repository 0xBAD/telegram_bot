import config
from lib.api import sendMessage


# сообщение в личку админу
def log(text):
    return sendMessage(chat_id=config.ADMIN_ID, text=text)