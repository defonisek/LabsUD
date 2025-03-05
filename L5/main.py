import psycopg2
import tkinter as tk
from tkinter import messagebox, ttk
import os

class BookstoreApp:
    def __init__(self, root):
        self.root = root
        root.title("Bookstore Database Manager")

        self.db_params = {
            'dbname': 'postgres',
            'user': 'postgres',
            'password': 'PASSWORD TO CHANGE', # Необходимо вставлять пароль пользователя с правами суперпользователя
            'host': 'localhost',
            'port': '5432',
            'client_encoding': 'utf8'
        }
        self.original_db_params = self.db_params.copy()
        self.postgres_superuser_params = self.db_params.copy()
        self.conn = None
        self.cursor = None

        db_mgmt_frame = ttk.Frame(root, padding=10)
        db_mgmt_frame.pack()
        
        ttk.Button(db_mgmt_frame, text="Создать базу данных", command=self.create_database).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(db_mgmt_frame, text="Удалить базу данных", command=self.drop_database).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(db_mgmt_frame, text="Открыть базу данных", command=self.open_database).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(db_mgmt_frame, text="Закрыть базу данных", command=self.close_database).grid(row=1, column=1, padx=5, pady=5)

        output_frame = ttk.Frame(root, padding=2)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        ttk.Label(output_frame, text="Вывод:").pack(anchor='w')
        self.output_text = tk.Text(output_frame, height=10, width=80)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.config(state=tk.DISABLED)

        operations_frame = ttk.Frame(root, padding=10)
        operations_frame.pack(fill=tk.X)

        left_col = ttk.Frame(operations_frame)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        ttk.Button(left_col, text="Очистить таблицу книг", command=self.clear_table).pack(padx=5, pady=5, fill=tk.X)
        
        self.add_book_frame = ttk.Frame(left_col)
        self.add_book_frame.pack(padx=5, pady=5, fill=tk.X)
        self.create_book_form(self.add_book_frame, "Добавить книгу", self.add_book)

        right_col = ttk.Frame(operations_frame)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)        

        search_frame = ttk.Frame(right_col)
        search_frame.pack(padx=5, pady=5, fill=tk.X)
        ttk.Label(search_frame, text="Поиск по названию:").pack(side=tk.LEFT)
        self.search_title_entry = ttk.Entry(search_frame)
        self.search_title_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Поиск", command=self.search_books).pack(side=tk.LEFT)

        self.delete_frame = ttk.Frame(right_col)
        self.delete_frame.pack(padx=5, pady=5, fill=tk.X)
        ttk.Label(self.delete_frame, text="Удалить по названию:").pack(side=tk.LEFT)
        self.delete_title_entry = ttk.Entry(self.delete_frame)
        self.delete_title_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(self.delete_frame, text="Удалить", command=self.delete_book).pack(side=tk.LEFT)

        self.update_book_frame = ttk.Frame(right_col)
        self.update_book_frame.pack(padx=5, pady=5, fill=tk.X)
        self.create_update_form()

        if not self.connect_to_db():
            root.destroy()

    def create_book_form(self, parent, button_text, command):
        fields = [
            ("Название:", "title_entry"),
            ("Автор:", "author_entry"),
            ("Жанр:", "genre_entry"),
            ("ISBN:", "isbn_entry"),
            ("Цена:", "price_entry"),
            ("Количество:", "quantity_entry")
        ]
        
        entries = []
        for i, (label, attr) in enumerate(fields):
            ttk.Label(parent, text=label).grid(row=i, column=0, padx=5, pady=2, sticky="e")
            entry = ttk.Entry(parent)
            entry.grid(row=i, column=1, padx=5, pady=2)
            setattr(self, attr, entry)
            entries.append(entry)
        
        ttk.Button(parent, text=button_text, command=command).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def create_update_form(self):
        ttk.Label(self.update_book_frame, text="ID книги:").grid(row=0, column=0, padx=5, pady=2, sticky="e")
        self.update_book_id_entry = ttk.Entry(self.update_book_frame)
        self.update_book_id_entry.grid(row=0, column=1, padx=5, pady=2)
        
        update_fields = [
            ("Новое название:", "update_title_entry"),
            ("Новый автор:", "update_author_entry"),
            ("Новый жанр:", "update_genre_entry"),
            ("Новый ISBN:", "update_isbn_entry"),
            ("Новая цена:", "update_price_entry"),
            ("Новое количество:", "update_quantity_entry")
        ]
        
        for i, (label, attr) in enumerate(update_fields, start=1):
            ttk.Label(self.update_book_frame, text=label).grid(row=i, column=0, padx=5, pady=2, sticky="e")
            entry = ttk.Entry(self.update_book_frame)
            entry.grid(row=i, column=1, padx=5, pady=2)
            setattr(self, attr, entry)
        
        ttk.Button(self.update_book_frame, text="Обновить книгу", command=self.update_book).grid(row=7, column=0, columnspan=2, pady=10)

    def open_database(self):
        if self.connect_to_db():
            self.output_message("Подключено к базе bookstore_db")
        self.db_params['dbname'] = 'bookstore_db'

    def close_database(self):
        self.db_params = self.original_db_params.copy()
        self.disconnect_from_db()
        self.output_message("Соединение с базой bookstore_db закрыто")


    def connect_to_db(self):
        try:
            self.conn = psycopg2.connect(**self.db_params)
            self.cursor = self.conn.cursor()
            self.output_message(f"Соединение установлено как суперпользователь: postgres")
            return True
        except psycopg2.OperationalError as e:
            messagebox.showerror("Ошибка подключения", f"Не удалось подключиться к базе данных.\nПроверьте настройки подключения.\nДетали: {e}")
            return False

    def disconnect_from_db(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()
            self.conn = None
            self.cursor = None
            self.output_message("Соединение с базой данных закрыто.")

    def call_function_fetch_results(self, function_name, params=None):
        if not self.conn:
            messagebox.showerror("Ошибка", "Нет соединения с базой данных.")
            return None
        try:
            if params:
                self.cursor.callproc(function_name, params)
            else:
                self.cursor.callproc(function_name)

            self.conn.commit()
            results = self.cursor.fetchall()
            return results
        except psycopg2.Error as e:
            self.conn.rollback()
            messagebox.showerror("Ошибка выполнения функции", f"Ошибка при выполнении функции {function_name}: {e}")
            self.output_message(f"Ошибка при выполнении функции {function_name}: {e}")
            return None


    def clear_table(self):
        if self.connect_to_db():
            results = self.call_function_fetch_results('clear_books_table_func')
            if results is not None:
                self.output_message("Таблица books успешно очищена.")
            self.disconnect_from_db()

    def add_book(self):
        if self.connect_to_db():
            title = self.title_entry.get()
            author = self.author_entry.get()
            genre = self.genre_entry.get()
            isbn = self.isbn_entry.get()
            try:
                price = float(self.price_entry.get())
                quantity = int(self.quantity_entry.get())
                params = (title, author, genre, isbn, price, quantity)
                results = self.call_function_fetch_results('add_new_book_func', params)
                if results is not None:
                    self.output_message(f"Книга '{title}' успешно добавлена.")
                    self.clear_input_fields(self.add_book_frame)
                else:
                    self.output_message(f"Ошибка при добавлении книги '{title}'.")
            except ValueError:
                messagebox.showerror("Ошибка ввода", "Неверный формат цены или количества.")
                self.output_message("Ошибка ввода: Неверный формат цены или количества.")
            self.disconnect_from_db()

    def search_books(self):
        if self.connect_to_db():
            search_term = self.search_title_entry.get()
            results = self.call_function_fetch_results('search_books_by_title_func', (search_term,))
            self.display_search_results(results)
            self.disconnect_from_db()

    def update_book(self):
        if self.connect_to_db():
            try:
                book_id = int(self.update_book_id_entry.get())
                title = self.update_title_entry.get()
                author = self.update_author_entry.get()
                genre = self.update_genre_entry.get()
                isbn = self.update_isbn_entry.get()
                price = float(self.update_price_entry.get())
                quantity = int(self.update_quantity_entry.get())
                params = (book_id, title, author, genre, isbn, price, quantity)
                results = self.call_function_fetch_results('update_book_info_func', params)
                if results is not None:
                    self.output_message(f"Информация о книге с ID {book_id} успешно обновлена.")
                    self.clear_input_fields(self.update_book_frame)
                else:
                    self.output_message(f"Ошибка при обновлении книги с ID {book_id}. Проверьте ID.")
            except ValueError:
                messagebox.showerror("Ошибка ввода", "Неверный формат ID, цены или количества.")
                self.output_message("Ошибка ввода: Неверный формат ID, цены или количества.")
            self.disconnect_from_db()

    def delete_book(self):
        if self.connect_to_db():
            title_to_delete = self.delete_title_entry.get()
            results = self.call_function_fetch_results('delete_book_by_title_func', (title_to_delete,))
            if results is not None:
                self.output_message(f"Книги с названием, содержащим '{title_to_delete}', удалены (если найдены).")
                self.clear_input_fields(self.delete_frame)
            else:
                self.output_message(f"Ошибка при удалении книг с названием, содержащим '{title_to_delete}'.")
            self.disconnect_from_db()

    def create_database(self):
        try:
            temp_conn_super = psycopg2.connect(**self.postgres_superuser_params) # Соединение для CREATE DATABASE
            temp_conn_super.autocommit = True
            temp_cursor_super = temp_conn_super.cursor()
            temp_cursor_super.execute("CREATE DATABASE bookstore_db;") # Прямой запрос, поскольку иначе невозможно
            temp_conn_super.commit()
            temp_cursor_super.close()
            temp_conn_super.close()
            self.output_message("База данных bookstore_db успешно создана.")
            messagebox.showinfo("Успех", "База данных bookstore_db успешно создана.")

            db_script_conn_params = self.db_params.copy()
            db_script_conn_params['dbname'] = 'bookstore_db'
            db_script_conn = psycopg2.connect(**db_script_conn_params)
            db_script_cursor = db_script_conn.cursor()
            script_dir = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(script_dir, 'bookstore_db_script.sql')
            try:
                with open(script_path, 'r', encoding='utf-8') as sql_file:
                    sql_script_content = sql_file.read()
                db_script_cursor.execute(sql_script_content)
                db_script_conn.commit()
                self.output_message("SQL скрипт bookstore_db_script.sql выполнен в базе данных bookstore_db.")
                messagebox.showinfo("Успех", "SQL скрипт выполнен в bookstore_db.")

                self.db_params['dbname'] = 'bookstore_db'
                self.output_message("Теперь подключение выполняется к базе данных bookstore_db.")
                self.disconnect_from_db()


            except Exception as script_e:
                db_script_conn.rollback()
                db_script_conn.close()
                messagebox.showerror("Ошибка выполнения SQL скрипта", f"Ошибка при выполнении SQL скрипта в bookstore_db:\n{script_e}")
                self.output_message(f"Ошибка при выполнении SQL скрипта в bookstore_db:\n{script_e}")
                return
            finally:
                db_script_conn.close()
            
            self.output_message("SQL скрипт bookstore_db_script.sql выполнен.")

        except Exception as e:
            messagebox.showerror("Ошибка создания БД", f"Не удалось создать базу данных: {e}")
            self.output_message(f"Не удалось создать базу данных: {e}")

    def drop_database(self):
        try:
            temp_conn = psycopg2.connect(**self.postgres_superuser_params)
            temp_conn.autocommit = True
            temp_cursor = temp_conn.cursor()
            temp_cursor.execute("SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = 'bookstore_db' AND pid <> pg_backend_pid();")
            temp_conn.commit()
            temp_cursor.execute("DROP DATABASE bookstore_db;")
            temp_conn.commit()
            temp_cursor.close()
            temp_conn.close()
            self.output_message("База данных bookstore_db успешно удалена.")
            messagebox.showinfo("Успех", "База данных bookstore_db успешно удалена.")

            self.db_params['dbname'] = 'postgres'
            self.disconnect_from_db()


        except Exception as e:
            messagebox.showerror("Ошибка удаления БД", f"Не удалось удалить базу данных: {e}")
            self.output_message(f"Не удалось удалить базу данных: {e}")

    def execute_sql_script(self, sql_file_path):
        if not self.conn:
            messagebox.showerror("Ошибка", "Нет соединения с базой данных.")
            return False

        try:
            with open(sql_file_path, 'r', encoding='utf-8') as sql_file:
                sql_script_content = sql_file.read()

            self.cursor.execute(sql_script_content)
            self.conn.commit()
            self.output_message(f"SQL скрипт из файла '{sql_file_path}' успешно выполнен.")
            messagebox.showinfo("Успех", "SQL скрипт выполнен.")
            return True

        except FileNotFoundError:
            messagebox.showerror("Ошибка", "Файл SQL скрипта не найден: " + sql_file_path)
            self.output_message("Файл SQL скрипта не найден: " + sql_file_path)
            return False
        except psycopg2.Error as e:
            self.conn.rollback()
            error_message = f"Ошибка при выполнении SQL скрипта:\n{e}"
            messagebox.showerror("Ошибка выполнения SQL скрипта", error_message)
            self.output_message(error_message)
            return False


    def display_search_results(self, results):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        if results:
            header = ["ID", "Название", "Автор", "Жанр", "ISBN", "Цена", "Количество"]
            self.output_text.insert(tk.END, "\t".join(header) + "\n")
            for row in results:
                self.output_text.insert(tk.END, "\t".join(map(str, row)) + "\n")
        else:
            self.output_text.insert(tk.END, "Книги не найдены.\n")
        self.output_text.config(state=tk.DISABLED)

    def output_message(self, message):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.config(state=tk.DISABLED)
        self.output_text.see(tk.END)

    def clear_input_fields(self, frame):
        for child in frame.winfo_children():
            if isinstance(child, ttk.Entry):
                child.delete(0, tk.END)


root = tk.Tk()
app = BookstoreApp(root)
root.protocol("WM_DELETE_WINDOW", app.disconnect_from_db)
root.mainloop()