tk.Label(self.content, text="Выбрать из шаблонов",
                 font=("Arial", 14)).pack()

        pattern_combo = ttk.Combobox(self.content)
        pattern_combo.pack()
        cur = self.db.connection.cursor()
        pattern_list = cur.execute("SELECT * from pattern ORDER BY name")
        if pattern_list:
            pattern_combo['values'] = [f"{ot['name']}" for ot in pattern_combo]


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
          bg="#072684", fg="white", width=20).pack(pady=20)