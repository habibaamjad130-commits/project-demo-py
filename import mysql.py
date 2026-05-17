# UPDATED PROFESSIONAL MALL EXPENSE MANAGEMENT SYSTEM
# =========================================================
# PROFESSIONAL MALL EXPENSE MANAGEMENT SYSTEM
# Dark Modern UI + Charts + Search + Reports + Stock
# =========================================================

# INSTALL FIRST:
# pip install customtkinter mysql-connector-python matplotlib pandas

import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import mysql.connector
from mysql.connector import Error

import matplotlib
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import pandas as pd
import datetime

# =========================================================
# APP SETTINGS
# =========================================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# =========================================================
# DATABASE CONFIG
# =========================================================
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "##@@",
    "database": "mall_expense_db"
}

# =========================================================
# DATABASE CONNECTION
# =========================================================
def connect_db():

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn

    except Error as e:
        messagebox.showerror("Database Error", str(e))
        return None

# =========================================================
# DATABASE SETUP
# =========================================================
def setup_database():

    temp = mysql.connector.connect(
        host="localhost",
        user="root",
        password="##@@"
    )

    cur = temp.cursor()

    cur.execute(
        "CREATE DATABASE IF NOT EXISTS mall_expense_db"
    )

    temp.commit()
    temp.close()

    conn = connect_db()
    cur = conn.cursor()

    # EXPENSE TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS expenses(
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255),
        amount DECIMAL(10,2),
        category VARCHAR(100),
        expense_date DATE,
        note TEXT
    )
    """)

    # ADMIN TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS admin(
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(100),
        password VARCHAR(100)
    )
    """)

    # STOCK TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS stock(
        id INT AUTO_INCREMENT PRIMARY KEY,
        product_name VARCHAR(255),
        quantity INT,
        price DECIMAL(10,2)
    )
    """)

    # DEFAULT ADMIN
    cur.execute("SELECT * FROM admin")

    if len(cur.fetchall()) == 0:

        cur.execute("""
        INSERT INTO admin(username,password)
        VALUES(%s,%s)
        """, ("admin", "admin123"))

    conn.commit()
    conn.close()

# =========================================================
# EXPENSE FUNCTIONS
# =========================================================
def add_expense(title, amount, category, date, note):

    conn = connect_db()

    if conn:

        cur = conn.cursor()

        cur.execute("""
        INSERT INTO expenses
        (title,amount,category,expense_date,note)
        VALUES(%s,%s,%s,%s,%s)
        """, (
            title,
            amount,
            category,
            date,
            note
        ))

        conn.commit()
        conn.close()


def get_expenses(search=""):

    conn = connect_db()

    if conn:

        cur = conn.cursor()

        if search:

            cur.execute("""
            SELECT * FROM expenses
            WHERE title LIKE %s
            OR category LIKE %s
            ORDER BY id DESC
            """, (
                f"%{search}%",
                f"%{search}%"
            ))

        else:

            cur.execute("""
            SELECT * FROM expenses
            ORDER BY id DESC
            """)

        rows = cur.fetchall()

        conn.close()

        return rows

    return []


def delete_expense(expense_id):

    conn = connect_db()

    if conn:

        cur = conn.cursor()

        cur.execute("""
        DELETE FROM expenses
        WHERE id=%s
        """, (expense_id,))

        conn.commit()
        conn.close()


def update_expense(expense_id, title, amount,
                   category, date, note):

    conn = connect_db()

    if conn:

        cur = conn.cursor()

        cur.execute("""
        UPDATE expenses
        SET title=%s,
            amount=%s,
            category=%s,
            expense_date=%s,
            note=%s
        WHERE id=%s
        """, (
            title,
            amount,
            category,
            date,
            note,
            expense_id
        ))

        conn.commit()
        conn.close()

# =========================================================
# STOCK FUNCTIONS
# =========================================================
def add_stock(product, quantity, price):

    conn = connect_db()

    if conn:

        cur = conn.cursor()

        cur.execute("""
        INSERT INTO stock
        (product_name,quantity,price)
        VALUES(%s,%s,%s)
        """, (
            product,
            quantity,
            price
        ))

        conn.commit()
        conn.close()


def get_stock():

    conn = connect_db()

    if conn:

        cur = conn.cursor()

        cur.execute("""
        SELECT * FROM stock
        ORDER BY id DESC
        """)

        rows = cur.fetchall()

        conn.close()

        return rows

    return []

# =========================================================
# LOGIN WINDOW
# =========================================================
class LoginWindow(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.geometry("500x550")
        self.title("Mall Expense Login")

        self.configure(fg_color="#020617")

        frame = ctk.CTkFrame(
            self,
            width=380,
            height=450,
            corner_radius=25,
            fg_color="#111827"
        )

        frame.place(relx=0.5,
                    rely=0.5,
                    anchor="center")

        title = ctk.CTkLabel(
            frame,
            text="🏬 ADMIN LOGIN",
            font=("Poppins", 30, "bold"),
            text_color="#38BDF8"
        )

        title.pack(pady=(45, 30))

        self.username = ctk.CTkEntry(
            frame,
            placeholder_text="Username",
            width=300,
            height=50,
            corner_radius=12
        )

        self.username.pack(pady=15)

        self.password = ctk.CTkEntry(
            frame,
            placeholder_text="Password",
            show="*",
            width=300,
            height=50,
            corner_radius=12
        )

        self.password.pack(pady=15)

        login_btn = ctk.CTkButton(
            frame,
            text="LOGIN",
            width=300,
            height=50,
            corner_radius=12,
            font=("Poppins", 16, "bold"),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self.login
        )

        login_btn.pack(pady=35)

        info = ctk.CTkLabel(
            frame,
            text="Default Login: admin / admin123",
            text_color="gray"
        )

        info.pack()

    def login(self):

        user = self.username.get()
        pas = self.password.get()

        conn = connect_db()

        if conn:

            cur = conn.cursor()

            cur.execute("""
            SELECT * FROM admin
            WHERE username=%s AND password=%s
            """, (user, pas))

            data = cur.fetchone()

            conn.close()

            if data:

                self.destroy()

                app = MallExpenseManager()
                app.mainloop()

            else:
                messagebox.showerror(
                    "Login Failed",
                    "Invalid Username or Password"
                )

# =========================================================
# MAIN APPLICATION
# =========================================================
class MallExpenseManager(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title(
            "Mall Expense Management System"
        )

        self.geometry("1550x900")

        self.configure(fg_color="#0F172A")

        self.selected_id = None

        self.categories = [
            "Food",
            "Shopping",
            "Transport",
            "Maintenance",
            "Salary",
            "Utilities",
            "Entertainment",
            "Other"
        ]

        self.build_ui()

        self.load_data()

        self.update_dashboard()

    # =====================================================
    # UI
    # =====================================================
    def build_ui(self):

        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Treeview",
            background="#0F172A",
            foreground="white",
            fieldbackground="#0F172A",
            rowheight=35,
            borderwidth=0,
            font=("Poppins", 11)
        )

        style.configure(
            "Treeview.Heading",
            background="#1E293B",
            foreground="white",
            font=("Poppins", 12, "bold")
        )

        # HEADER
        header = ctk.CTkFrame(
            self,
            height=80,
            fg_color="#111827",
            corner_radius=0
        )

        header.pack(fill="x")

        title = ctk.CTkLabel(
            header,
            text="🏬 Mall Expense Management",
            font=("Poppins", 30, "bold")
        )

        title.pack(side="left",
                   padx=25,
                   pady=20)

        date_label = ctk.CTkLabel(
            header,
            text=datetime.datetime.now().strftime(
                "%d %B %Y"
            ),
            font=("Poppins", 15)
        )

        date_label.pack(side="right",
                        padx=25)

        # MAIN FRAME
        main = ctk.CTkFrame(
            self,
            fg_color="#0F172A"
        )

        main.pack(fill="both",
                  expand=True)

        # SIDEBAR
        sidebar = ctk.CTkFrame(
            main,
            width=230,
            fg_color="#020617",
            corner_radius=0
        )

        sidebar.pack(side="left",
                     fill="y")

        logo = ctk.CTkLabel(
            sidebar,
            text="🏬 MALL SYSTEM",
            font=("Poppins", 22, "bold"),
            text_color="#38BDF8"
        )

        logo.pack(pady=30)

        menu_buttons = [
            ("Dashboard", None),
            ("Charts", self.show_chart),
            ("Export CSV", self.export_csv),
            ("Stock", self.stock_window),
            ("Theme", self.change_theme),
            ("Logout", self.destroy)
        ]

        for text, command in menu_buttons:

            btn = ctk.CTkButton(
                sidebar,
                text=text,
                width=180,
                height=45,
                fg_color="#1E293B",
                hover_color="#2563EB",
                font=("Poppins", 15, "bold"),
                corner_radius=12,
                command=command
            )

            btn.pack(pady=10)

        # CONTENT
        content = ctk.CTkFrame(
            main,
            fg_color="#0F172A"
        )

        content.pack(side="left",
                     fill="both",
                     expand=True)

        # DASHBOARD CARDS
        cards = ctk.CTkFrame(
            content,
            fg_color="#0F172A"
        )

        cards.pack(fill="x",
                   pady=20)

        self.total_card = self.create_card(
            cards,
            "Total Expense",
            "0"
        )

        self.total_card.pack(side="left",
                             padx=15)

        self.count_card = self.create_card(
            cards,
            "Total Records",
            "0"
        )

        self.count_card.pack(side="left",
                             padx=15)

        self.today_card = self.create_card(
            cards,
            "Today Expense",
            "0"
        )

        self.today_card.pack(side="left",
                             padx=15)

        # SEARCH BAR
        search_frame = ctk.CTkFrame(
            content,
            fg_color="#0F172A"
        )

        search_frame.pack(fill="x",
                          padx=15)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search Expense...",
            width=350,
            height=40
        )

        self.search_entry.pack(side="right")

        search_btn = ctk.CTkButton(
            search_frame,
            text="SEARCH",
            width=120,
            command=self.search_data
        )

        search_btn.pack(side="right",
                        padx=10)

        # FORM
        form = ctk.CTkFrame(
            content,
            fg_color="#111827",
            corner_radius=15
        )

        form.pack(fill="x",
                  padx=15,
                  pady=10)

        self.title_entry = ctk.CTkEntry(
            form,
            placeholder_text="Expense Title",
            width=220,
            height=45
        )

        self.title_entry.grid(row=0,
                              column=0,
                              padx=10,
                              pady=20)

        self.amount_entry = ctk.CTkEntry(
            form,
            placeholder_text="Amount",
            width=170,
            height=45
        )

        self.amount_entry.grid(row=0,
                               column=1,
                               padx=10)

        self.category_box = ctk.CTkComboBox(
            form,
            values=self.categories,
            width=180,
            height=45
        )

        self.category_box.grid(row=0,
                               column=2,
                               padx=10)

        self.note_entry = ctk.CTkEntry(
            form,
            placeholder_text="Note",
            width=250,
            height=45
        )

        self.note_entry.grid(row=0,
                             column=3,
                             padx=10)

        add_btn = ctk.CTkButton(
            form,
            text="ADD",
            width=120,
            height=45,
            fg_color="#16A34A",
            command=self.add_data
        )

        add_btn.grid(row=0,
                     column=4,
                     padx=10)

        update_btn = ctk.CTkButton(
            form,
            text="UPDATE",
            width=120,
            height=45,
            fg_color="#2563EB",
            command=self.update_data
        )

        update_btn.grid(row=0,
                        column=5,
                        padx=10)

        delete_btn = ctk.CTkButton(
            form,
            text="DELETE",
            width=120,
            height=45,
            fg_color="#DC2626",
            command=self.delete_data
        )

        delete_btn.grid(row=0,
                        column=6,
                        padx=10)

        # TABLE
        table_frame = ctk.CTkFrame(
            content,
            fg_color="#111827",
            corner_radius=15
        )

        table_frame.pack(fill="both",
                         expand=True,
                         padx=15,
                         pady=15)

        columns = (
            "ID",
            "Title",
            "Amount",
            "Category",
            "Date",
            "Note"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=18
        )

        for col in columns:

            self.tree.heading(col,
                              text=col)

            self.tree.column(col,
                             width=170)

        self.tree.pack(fill="both",
                       expand=True)

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.select_data
        )

    # =====================================================
    # CARD
    # =====================================================
    def create_card(self,
                    parent,
                    title,
                    value):

        card = ctk.CTkFrame(
            parent,
            width=280,
            height=120,
            fg_color="#111827",
            corner_radius=18
        )

        card.pack_propagate(False)

        label1 = ctk.CTkLabel(
            card,
            text=title,
            font=("Poppins", 18)
        )

        label1.pack(pady=(20, 5))

        label2 = ctk.CTkLabel(
            card,
            text=value,
            font=("Poppins", 28, "bold"),
            text_color="#38BDF8"
        )

        label2.pack()

        card.value_label = label2

        return card

    # =====================================================
    # ADD DATA
    # =====================================================
    def add_data(self):

        title = self.title_entry.get()
        amount = self.amount_entry.get()
        category = self.category_box.get()
        note = self.note_entry.get()

        if title == "" or amount == "":
            messagebox.showerror(
                "Error",
                "Fill all fields"
            )
            return

        add_expense(
            title,
            amount,
            category,
            datetime.date.today(),
            note
        )

        messagebox.showinfo(
            "Success",
            "Expense Added Successfully"
        )

        self.load_data()
        self.update_dashboard()
        self.clear_fields()

    # =====================================================
    # LOAD DATA
    # =====================================================
    def load_data(self, search=""):

        for row in self.tree.get_children():
            self.tree.delete(row)

        rows = get_expenses(search)

        for row in rows:
            self.tree.insert("", "end",
                             values=row)

    # =====================================================
    # SEARCH
    # =====================================================
    def search_data(self):

        keyword = self.search_entry.get()
        self.load_data(keyword)

    # =====================================================
    # SELECT DATA
    # =====================================================
    def select_data(self, event):

        selected = self.tree.focus()

        data = self.tree.item(selected)

        row = data["values"]

        if row:

            self.selected_id = row[0]

            self.title_entry.delete(0, "end")
            self.title_entry.insert(0, row[1])

            self.amount_entry.delete(0, "end")
            self.amount_entry.insert(0, row[2])

            self.category_box.set(row[3])

            self.note_entry.delete(0, "end")
            self.note_entry.insert(0, row[5])

    # =====================================================
    # UPDATE
    # =====================================================
    def update_data(self):

        if self.selected_id is None:
            return

        update_expense(
            self.selected_id,
            self.title_entry.get(),
            self.amount_entry.get(),
            self.category_box.get(),
            datetime.date.today(),
            self.note_entry.get()
        )

        messagebox.showinfo(
            "Updated",
            "Expense Updated Successfully"
        )

        self.load_data()
        self.update_dashboard()
        self.clear_fields()

    # =====================================================
    # DELETE
    # =====================================================
    def delete_data(self):

        if self.selected_id is None:
            return

        delete_expense(self.selected_id)

        messagebox.showinfo(
            "Deleted",
            "Expense Deleted Successfully"
        )

        self.load_data()
        self.update_dashboard()
        self.clear_fields()

    # =====================================================
    # DASHBOARD
    # =====================================================
    def update_dashboard(self):

        rows = get_expenses()

        total = 0
        today_total = 0

        today = str(datetime.date.today())

        for row in rows:

            total += float(row[2])

            if str(row[4]) == today:
                today_total += float(row[2])

        self.total_card.value_label.configure(
            text=f"Rs {total}"
        )

        self.count_card.value_label.configure(
            text=str(len(rows))
        )

        self.today_card.value_label.configure(
            text=f"Rs {today_total}"
        )

    # =====================================================
    # CHARTS
    # =====================================================
    def show_chart(self):

        data = get_expenses()

        if not data:

            messagebox.showinfo(
                "No Data",
                "No expense data available"
            )

            return

        categories = {}

        for row in data:

            category = row[3]
            amount = float(row[2])

            if category in categories:
                categories[category] += amount
            else:
                categories[category] = amount

        fig, ax = plt.subplots(figsize=(7, 6))

        ax.pie(
            categories.values(),
            labels=categories.keys(),
            autopct="%1.1f%%"
        )

        ax.set_title("Expense Categories")

        chart_window = ctk.CTkToplevel(self)

        chart_window.title("Expense Charts")

        chart_window.geometry("800x650")

        canvas = FigureCanvasTkAgg(
            fig,
            master=chart_window
        )

        canvas.draw()

        canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

    # =====================================================
    # EXPORT CSV
    # =====================================================
    def export_csv(self):

        rows = get_expenses()

        if not rows:
            messagebox.showerror(
                "No Data",
                "No expense data found"
            )
            return

        df = pd.DataFrame(rows, columns=[
            "ID",
            "Title",
            "Amount",
            "Category",
            "Date",
            "Note"
        ])

        file = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV File", "*.csv")]
        )

        if file:

            df.to_csv(file, index=False)

            messagebox.showinfo(
                "Exported",
                "CSV Export Successful"
            )

    # =====================================================
    # STOCK WINDOW
    # =====================================================
    def stock_window(self):

        stock_win = ctk.CTkToplevel(self)

        stock_win.title("Stock Management")

        stock_win.geometry("950x700")

        title = ctk.CTkLabel(
            stock_win,
            text="📦 STOCK MANAGEMENT",
            font=("Poppins", 28, "bold")
        )

        title.pack(pady=20)

        product_entry = ctk.CTkEntry(
            stock_win,
            placeholder_text="Product Name",
            width=250,
            height=45
        )

        product_entry.pack(pady=10)

        qty_entry = ctk.CTkEntry(
            stock_win,
            placeholder_text="Quantity",
            width=250,
            height=45
        )

        qty_entry.pack(pady=10)

        price_entry = ctk.CTkEntry(
            stock_win,
            placeholder_text="Price",
            width=250,
            height=45
        )

        price_entry.pack(pady=10)

        tree = ttk.Treeview(
            stock_win,
            columns=("ID",
                     "Product",
                     "Qty",
                     "Price"),
            show="headings"
        )

        tree.heading("ID", text="ID")
        tree.heading("Product", text="Product")
        tree.heading("Qty", text="Quantity")
        tree.heading("Price", text="Price")

        tree.pack(fill="both",
                  expand=True,
                  pady=20)

        def load_stock():

            for row in tree.get_children():
                tree.delete(row)

            rows = get_stock()

            for row in rows:
                tree.insert("", "end",
                            values=row)

        def save_stock():

            if product_entry.get() == "":
                return

            add_stock(
                product_entry.get(),
                qty_entry.get(),
                price_entry.get()
            )

            load_stock()

            messagebox.showinfo(
                "Success",
                "Stock Added Successfully"
            )

        btn = ctk.CTkButton(
            stock_win,
            text="ADD STOCK",
            fg_color="#16A34A",
            width=220,
            height=45,
            command=save_stock
        )

        btn.pack(pady=10)

        load_stock()

    # =====================================================
    # THEME
    # =====================================================
    def change_theme(self):

        current = ctk.get_appearance_mode()

        if current == "Dark":
            ctk.set_appearance_mode("light")

        else:
            ctk.set_appearance_mode("dark")

    # =====================================================
    # CLEAR
    # =====================================================
    def clear_fields(self):

        self.selected_id = None

        self.title_entry.delete(0, "end")
        self.amount_entry.delete(0, "end")
        self.note_entry.delete(0, "end")

# =========================================================
# START APP
# =========================================================
if __name__ == "__main__":

    setup_database()

    login = LoginWindow()

    login.mainloop()