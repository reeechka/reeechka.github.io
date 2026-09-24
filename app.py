import tkinter as tk
from tkinter import ttk, messagebox, filedialog, PhotoImage, Image
import os
from psycopg2 import connect

from db import Database
from auth import Auth

class MainWindow:
    def __init__(self, db, user_data):
        self.db = db
        self.user_data = user_data
        self.group_id = None

        self.root = tk.Tk()
        self.root.geometry("800x600")
        self.root.configure(bg="#ABE2F4")
        self.root.title("Сервис рассылок")

        self.create_widgets()
        # ПРАВАЯ ОБЛАСТЬ СО СКРОЛЛОМ


        # Показываем главную страницу
        self.main_page()

    def _on_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(1, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    def create_widgets(self):
        # хедер
        header = tk.Frame(self.root, bg="#072684", height=70)
        header.pack(side='top', fill='x')
        header.pack_propagate(False)

        tk.Label(header, text="Панель администратора",
                 fg='white', bg='#072684',
                 font=("Arial", 20, "bold")).pack(side='left', padx=20)

        # основной фрейм
        main_frame = tk.Frame(self.root, bg="#ABE2F4")
        main_frame.pack(side='top', expand=True, fill='both')

        # сайдбар
        sidebar = tk.Frame(main_frame, bg="#072684", width=200)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)

        btn_style = {"bg": "#072684", "fg": "white", "width": 18, "font": ("Arial", 12, "bold")}

        tk.Button(sidebar, text="Главная", command=self.main_page, **btn_style).pack(pady=10)
        tk.Button(sidebar, text="Создать рассылку", command=self.create_mail, **btn_style).pack(pady=10)
        tk.Button(sidebar, text="Мои рассылки", command=self.view_mail, **btn_style).pack(pady=10)
        tk.Button(sidebar, text="Создать шаблон", command=self.create_pattern, **btn_style).pack(pady=10)
        tk.Button(sidebar, text="Создать группу", command=self.check_group, **btn_style).pack(pady=10)
        tk.Button(sidebar, text="Группы адресатов", command=self.view_group, **btn_style).pack(pady=10)

        right_container = tk.Frame(main_frame, bg="#F0F0F0")
        right_container.pack(side='left', expand=True, fill='both')

        # Canvas и Scrollbar
        self.canvas = tk.Canvas(right_container, bg="#F0F0F0", highlightthickness=0)
        scrollbar = tk.Scrollbar(right_container, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Внутренний фрейм (всё содержимое будет здесь)
        self.content = tk.Frame(self.canvas, bg="#F0F0F0")
        self.canvas.create_window((0, 0), window=self.content, anchor='nw')

        # Обновление скролла
        self.content.bind('<Configure>', self._on_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)

        # Колесо мыши
        self.canvas.bind('<MouseWheel>', self._on_mousewheel)

    def clear(self):
        for w in self.content.winfo_children():
            w.destroy()

    def main_page(self):
        self.clear()
        tk.Label(self.content, text=f"Добро пожаловать, {self.user_data[1]}!",
                 font=("Arial", 17, "bold")).pack(anchor='w', pady=10, padx=10)
        cursor = self.db.connection.cursor()
        cursor.execute("SELECT COUNT(*) from groups where id_admin = %s", (self.user_data[0],))
        count_group = cursor.fetchone()[0]

        tk.Label(self.content, text=f"Созданных вами групп {count_group}",
                 font=("Arial", 14)).pack(anchor='w', pady=10, padx=10)

        cursor.execute("SELECT COUNT(*) from mailing where id_admin = %s", (self.user_data[0],))
        count_mail = cursor.fetchone()[0]

        tk.Label(self.content, text=f"Созданных вами рассылок {count_mail}",
                 font=("Arial", 14)).pack(anchor='w', pady=10, padx=10)



    def create_mail(self):
        self.clear()
        tk.Label(self.content, text="Создать рассылку",
                 font=("Arial", 17, "bold")).pack(pady=(10, 10))

        tk.Label(self.content, text="Получатели",
                 font=("Arial", 14)).pack(pady=10)
        #Выбор получателей
        self.group_combo = ttk.Combobox(self.content)
        self.group_combo.pack(pady=10)
        cur = self.db.connection.cursor()
        group_list = cur.execute("SELECT * from groups ORDER BY name")
        groups = cur.fetchall()
        if groups:
            self.group_combo['values'] = [''] + [f"{ot[1]}" for ot in groups]
            self.group_combo.set('')

        #ВЫБОР ШАБЛОНА
        tk.Label(self.content, text="Выбрать шаблон",
                 font=("Arial", 14)).pack(pady=10)
        self.pattern_combo = ttk.Combobox(self.content, width=40, state = "readonly")
        self.pattern_combo.pack()
        cursor = self.db.connection.cursor()
        cursor.execute("SELECT * from pattern where id_admin = %s", (self.user_data[0],))
        pattern = cursor.fetchall()
        if pattern:
            self.pattern_combo['values'] = [''] + [f"{ot[4]}" for ot in pattern]
            self.pattern_combo.set('')
            pattern_data = {p[4]: {'id': p[0], 'name': p[2], 'text': p[3]} for p in pattern}
        else:
            pattern_data = {}



        tk.Label(self.content, text="Тема",
                 font=("Arial", 14)).pack(pady=10)
        self.name_entry = tk.Entry(self.content, font=("Arial", 12))
        self.name_entry.pack()

        tk.Label(self.content, text="Текст",
                 font=("Arial", 14)).pack(pady=10)
        self.text_entry = tk.Text(self.content, font=("Arial", 12), width=50, height=10)
        self.text_entry.pack()


        def on_pattern_select(event):
            selected = self.pattern_combo.get()
            if selected and selected in pattern_data:
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, pattern_data[selected]['name'])
                self.text_entry.delete("1.0", tk.END)
                self.text_entry.insert("1.0", pattern_data[selected]['text'])
            elif not selected:
                self.name_entry.delete(0, tk.END)
                self.text_entry.delete("1.0", tk.END)

        self.pattern_combo.bind('<<ComboboxSelected>>', on_pattern_select)


        #добавить фото
        tk.Label(self.content, text="Изображение",
                 font=("Arial", 14)).pack(pady=10)


        tk.Button(self.content, text="Добавить фото",
                  fg="white",
                  bg="#072684",
                  width=15,
                  font=("Arial", 12),
                  command=self.add_photo).pack(pady=10)

        self.photo_frame = tk.Frame(self.content)
        self.photo_frame.pack()
        self.image_label= tk.Label(self.photo_frame)
        self.image_label.pack()



        tk.Button(self.content, text="Удалить фото",
                  fg="white",
                  bg="#072684",
                  width=15,
                  font=("Arial", 12),
                  command=self.clear_photo).pack(pady=10)
        tk.Button(self.content, text="Отправить",
                  fg="white",
                  bg="#072684",
                  width=15,
                  font=("Arial", 12),
                  command=self.save).pack(pady=10)
    def save(self):
            cursor = self.db.connection.cursor()
            name = self.name_entry.get().strip()
            text = self.text_entry.get("1.0", tk.END).strip()
            image_path = self.current_image_path if hasattr(self, 'current_image_path') else None
            if not name or not text:
                messagebox.showerror("Ошибка!", "Заполните все поля!")
                return

            pattern_name = self.pattern_combo.get()
            pattern_id = None
            if pattern_name:
                cursor.execute("SELECT ID from pattern where name = %s and id_user = %s", (pattern_name, self.user_data[0]))
                pattern = cursor.fetchone()
                if pattern:
                    pattern_id = pattern[0]

            group_name = self.group_combo.get()

            if group_name:
                cursor.execute("SELECT id from groups where name = %s",
                               (group_name,))
                group = cursor.fetchone()
                if group:
                    self.group_id = group[0]
            cursor.execute("INSERT INTO mailing(id_group, id_pattern, theme, text, photo, id_admin) VALUES(%s, %s, %s, %s, %s, %s)", (self.group_id, pattern_id, name, text, image_path, self.user_data[0]  ))
            self.db.connection.commit()
            cur = self.db.connection.cursor()
            cur.execute("""select g.name, STRING_AGG(a.login, ', ') as logins from groups g 
                        LEFT JOIN groups_recipients gr ON g.id = gr.id_group
                        left join admin a ON gu.user_id = u.user_id where g.id = %s GROUP BY g.id""", (self.group_id,))
            res = cur.fetchone()
            group_name = res[0]
            count = res[1]


            messagebox.showinfo("Успех!", f"Рассылка для группы {group_name} отправлена для получателей: {count} !")
            self.name_entry.delete(0, tk.END)
            self.text_entry.delete("1.0", tk.END)
            self.pattern_combo.set('')
            self.group_combo.set('')
            if image_path:
                self.clear_photo()



    def add_photo(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png;*.gif")]
        )
        if not file_path:
            return

        try:
            self.photo = None
            self.photo = tk.PhotoImage(file=file_path)
            self.image_label.pack(pady=10)
            # Масштабирование через свойства Label (ограничение по ширине)
            self.image_label.config(
                image=self.photo,
                width=200,  # Макс. ширина
                height=150,  # Макс. высота
                bg="white",
                relief="solid",  # Исправленная опечатка
                bd=1
            )
            self.current_image_path = file_path
            messagebox.showinfo("Успех", "Изображение загружено!")
        except tk.TclError:
            messagebox.showerror(
                "Ошибка",
                "Формат изображения не поддерживается.\n"
                "Используйте PNG или GIF."
            )

    def clear_photo(self):
        self.image_label.pack_forget()
        # Очищаем изображение в Label
        self.image_label.config(image="")
        # Обнуляем ссылку на PhotoImage для освобождения памяти
        self.photo = None
        # Сбрасываем путь к файлу
        self.current_image_path = None

        # Визуальная обратная связь
        messagebox.showinfo("Успех", "Изображение удалено")


    def send_mail(self):
         pass


    def view_mail(self):
        self.clear()
        tk.Label(self.content, text="Мои рассылки", font=("Arial", 17, "bold")).pack(pady=10)
        table_frame = tk.Frame(self.content)
        table_frame.pack(expand=True, fill='both', padx=10, pady=10)
        scrollbar = tk.Scrollbar(table_frame)
        scrollbar.pack(side='right', fill='y')
        columns = ("id", "name", "group_name", "created_at")
        self.tree = ttk.Treeview(table_frame, columns = columns, show="headings", yscrollcommand=scrollbar.set, height=15)
        self.tree.heading("id", text="№")
        self.tree.heading("name", text="Тема")
        self.tree.heading("group_name", text="Группа")
        self.tree.heading("created_at", text="Дата отправки")

        self.tree.pack(side='left',fill='both', expand=True)
        scrollbar.config(command=self.tree.yview)
        self.load_mail()

    def load_mail(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        cursor = self.db.connection.cursor()
        cursor.execute("""
                SELECT m.id, m.theme, g.name as group_name
                FROM mail m 
                LEFT JOIN groups g ON m.id_group = g.id
                WHERE m.id_admin = %s
            """, (self.user_data[0],))
        mails = cursor.fetchall()
        for mail in mails:
            self.tree.insert("", "end", values=(
                mail[0],
                mail[1],
                mail[2],
            ))



    def create_pattern(self):
        self.clear()

        tk.Label(self.content, text="Создать шаблон", font=("Arial", 17, "bold"), bg="#F0F0F0").pack(pady=10)

        # Название шаблона
        tk.Label(self.content, text="Название шаблона", font=("Arial", 14), bg="#F0F0F0").pack(pady=10)
        pattern_name_entry = tk.Entry(self.content, font=("Arial", 12))
        pattern_name_entry.pack()

        # Тема
        tk.Label(self.content, text="Тема", font=("Arial", 14), bg="#F0F0F0").pack(pady=10)
        subject_entry = tk.Entry(self.content, font=("Arial", 12))
        subject_entry.pack()

        # Текст
        tk.Label(self.content, text="Текст", font=("Arial", 14), bg="#F0F0F0").pack(pady=10)
        text_entry = tk.Text(self.content, font=("Arial", 12), width=50, height=10)
        text_entry.pack()


        # Кнопка сохранения
        def save():
            name_pattern = pattern_name_entry.get().strip()
            name = subject_entry.get().strip()
            text = text_entry.get("1.0", tk.END).strip()

            if not name_pattern or not name or not text:
                messagebox.showerror("Ошибка", "Заполните все поля")
                return

            cursor = self.db.connection.cursor()
            cursor.execute(
                "INSERT INTO pattern (id_user, name, text, name_pattern) VALUES (%s, %s, %s, %s)",
                (self.user_data[0], name, text, name_pattern)
            )
            self.db.connection.commit()
            messagebox.showinfo("Успех", "Шаблон сохранён")
            pattern_name_entry.delete(0, tk.END)
            subject_entry.delete(0, tk.END)
            text_entry.delete("1.0", tk.END)

        tk.Button(self.content, text="Сохранить шаблон", command=save,
                  font=("Arial, 12"),
                  bg="#072684", fg="white", width=20).pack(pady=20)


    def check_group(self):
        self.clear()
        tk.Label(self.content, text="Создать группу адресатов", font=("Arial", 17, "bold")).pack(pady=10)
        name = tk.Label(self.content, text="Название группы", font=("Arial", 14)).pack(pady=10)
        self.name_entry = tk.Entry(self.content, font=("Arial", 12))
        self.name_entry.pack(pady=10)
        tk.Label(self.content, text="Выберете получателей", font=("Arial", 14)).pack(pady=10)
        #список пользователей

        #контейнер ждля канвас
        container = tk.Frame(self.content)
        container.pack()
        #скролбар
        canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        list = tk.Frame(canvas)
        canvas.create_window((0, 0), window=list, anchor='nw')




        def update_scroll(event):
            canvas.configure(scrollregion=canvas.bbox('all'))

        list.bind('<Configure>', update_scroll)

        cursor = self.db.connection.cursor()
        cursor.execute("SELECT user_id, login from users where role = 'client'")
        users = cursor.fetchall()
        if not users:
            tk.Label(self.content, text="Пользователей нет!", font=("Arial", 14, "bold")).pack()
        else:

            self.recipient_vars = {}

            for user in users:
                self.user_id = user[0]
                login = user[1]

                var = tk.BooleanVar()
                self.recipient_vars[user[0]] = var

                # Текст
                display_text = f"ID {user[0]}"
                if user[1]:
                    display_text += f" {user[1]}"
                cb = tk.Checkbutton(list, variable=var, bg="#F0F0F0",
                                    font=("Arial", 11), text=display_text)
                cb.pack(anchor='w', padx=20, pady=2)



        tk.Button(self.content, text="Сохранить", fg="white",
                  bg="#072684",
                  width=15,

                  font=("Arial", 12), command = self.save_group).pack(pady=(10,10))
    def save_group(self):
            cursor = self.db.connection.cursor()
            group_name = self.name_entry.get()
            if not group_name:
                messagebox.showerror("Ошибка!", "Введите название группы!")
                return
            selected_ids = [uid for uid, var in self.recipient_vars.items() if var.get()]

            if not selected_ids:
                messagebox.showerror("Ошибка", "Выберите хотя бы одного получателя")
                return
            cursor.execute("INSERT INTO groups(name, id_user) VALUES(%s, %s) RETURNING id", (group_name, self.user_data[0]))
            group_id = cursor.fetchone()[0]
            for user_id in selected_ids:
                cursor.execute("INSERT INTO group_user (group_id, user_id) VALUES (%s, %s)",(group_id, user_id))
            self.db.connection.commit()
            messagebox.showinfo("Успех",
                                    f"Группа '{group_name}' создана!\nДобавлено получателей: {len(selected_ids)}")

            self.name_entry.delete(0, tk.END)
            for var in self.recipient_vars.values():
                var.set(False)

    def view_group(self):
            self.clear()
            tk.Label(self.content, text="Группы адресатов", font=("Arial", 17, "bold")).pack(pady=10)

            cur = self.db.connection.cursor()
            cur.execute("""select g.name, STRING_AGG(u.login, ', ') as logins from groups g 
                                    LEFT JOIN group_user gu ON g.id = gu.group_id 
                                    left join users u ON gu.user_id = u.user_id where g.id_user = %s GROUP BY g.name""",
                        (self.user_data[0],))
            res = cur.fetchall()
            for r in res:
                group_name = r[0]
                login = r[1]


                group_frame = tk.Frame(self.content, relief="groove", bd=5)
                group_frame.pack(fill='x', padx=20, pady=10)

                tk.Label(group_frame, text=f"{group_name}",
                         font=("Arial", 14, "bold"), fg='#072684').pack(anchor='w', padx=10, pady=5)

                tk.Label(group_frame, text=f"Участники: {login}",
                         font=("Arial", 12)).pack(anchor='w', padx=10, pady=5)




















