from lib.logger import log
from lib.recordset import DB


class User:
    user_id = None
    first_name = None
    last_name = None
    username = None
    language_code = None

    def __init__(self, user_id, first_name, last_name, username, language_code):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.language_code = language_code


class Message:
    message_id = None
    text = None
    chat_id = None
    date = None
    from_id = None

    def __init__(self, message_id, text, chat_id, date, from_id):
        self.message_id = message_id
        self.text = text
        self.chat_id = chat_id
        self.date = date
        self.from_id = from_id


class DBStat(object):
    db = None

    def __init__(self):
        self.db = DB(db_name="podbot")

    def check_user(self, user_id):
        sql = "select 1 as res from tgrm_users where id= %s "
        return self.db.cursor.execute(sql, user_id)

    def add_new_user(self, user=User):
        try:
            sql = "insert into tgrm_users set id= %s , " \
                  "first_name = %s , " \
                  "last_name= %s, " \
                  "username= %s , " \
                  "language_code= %s "

            if self.db.cursor.execute(sql, (user.user_id,user.first_name,user.last_name,user.username,user.language_code)):
                self.db.commit()

        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            log(tb)

    def add_new_message(self, message=Message):
        sql = '''insert into messages SET 
                  text = %s, chat_id = %s, date = %s, from_id = %s
                  '''
        if self.db.cursor.execute(sql, (message.text, message.chat_id, message.date, message.from_id)):
            self.db.commit()

