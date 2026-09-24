from db import Database
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk

class Auth:
    def __init__(self, db):
        self.db = db
        self.user_data = None
        self.is_auth = False
        self.root = tk.Tk()
        self.root.configure(bg="#ABE2F4")
        self.root.geometry("500x300")
        self.root.title("Сервис рассылок. Авторизация")

        self.create_widgets() #виджеты

    def create_widgets(self):

        self.frm = tk.Frame(self.root, bg="#F0F0F0")
        self.frm.pack(pady=20, ipadx=10, ipady=10, anchor="center")

        tk.Label(self.frm, text="Авторизация",
                 font=("Arial", 16, "bold")).pack(pady=(15,0))

        tk.Label(self.frm, text="Логин",
                 font=("Arial", 14)).pack(pady=(5,3))
        self.login_entry = tk.Entry(self.frm, width=20, font=("Arial", 12))
        self.login_entry.pack(pady=10)

        tk.Label(self.frm, text="Пароль",
                 font=("Arial", 14)).pack(pady=(5, 3))
        self.password_entry = tk.Entry(self.frm, show="*", width=20, font=("Arial", 12))
        self.password_entry.pack(pady=10)

        tk.Button(self.frm, text="Войти",
                  fg="white",
                  bg="#072684",
                  width=15,
                  font=("Arial", 12),
                  command = self.login).pack()

    def login(self):
        login = self.login_entry.get()
        password = self.password_entry.get()

        cursor = self.db.connection.cursor()
        cursor.execute(

            "SELECT * FROM admin where login = %s AND password = %s", (login, password)

        )

        user = cursor.fetchone()

        if user:
            self.is_auth = True
            self.user_data = user
            self.root.destroy()
        elif not password or not login:
            messagebox.showerror("Ошибка", "Заполните все поля")
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль!")
