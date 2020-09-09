import pymysql
import config


class DB:
    db = None
    cursor = None

    def __init__(self, db_host=config.db_host, db_user=config.db_user, db_password=config.db_password,
                 db_name=config.db_name):
        self.db = pymysql.connect(host=db_host, user=db_user, passwd=db_password, db=db_name,
                                  charset='utf8')
        self.cursor = self.db.cursor()

    def execute(self, sql='', binds=None):
        self.cursor.execute(sql, binds)

    def commit(self):
        self.db.commit()

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def close(self):
        self.db.close()

    def __delete__(self, instance):
        self.close()
