import psycopg2
from tkinter import messagebox
from pyexpat.errors import messages

class Database:
    def __init__(self, dbname, user, password, host, port):
        self.dbname =dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None

    def connect(self): #создание соединения
        try:
            self.connection = psycopg2.connect(
                dbname = self.dbname,
                user = self.user,
                password = self.password,
                host = self.host,
                port = self.port
            )
            print("Подключение успешно!")
            return self.connection
        except psycopg2.Error as e:
            print(e)
            messagebox.showerror("Ошибка!", e)
    def close(self): #закрываем соединение
        if self.connection:
            self.connection.close()
            print("Подключение закрыто!")




