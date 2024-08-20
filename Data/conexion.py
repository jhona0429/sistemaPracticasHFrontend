import pymysql
import pymysql.cursors


class conexion:
    host="localhost"
    user="root"
    passwd="admin"
    database="sistemaventa"
    db=None

    def __init__(self):
        self.db = pymysql.connect(host=self.host,
                                        user=self.user,
                                        password=self.passwd,
                                        database=self.database,
                                        cursorclass=pymysql.cursors.DictCursor)
    def getConexion(self):
        return self.db 