import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("700x500")
        self.data_file = "data/expenses.json"
        self.expenses = []
        self.load_data()

        # --- ВИДЖЕТЫ ---
        # Поля ввода
        ttk.Label(root, text="Сумма:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.amount_entry = ttk.Entry(root, width=15)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(root, text="Категория:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.category_entry = ttk.Entry(root, width=15)
        self.category_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(root, text="Дата (ГГГГ-ММ-ДД):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.date_entry = ttk.Entry(root, width=15)
        self.date_entry.grid(row=2, column=1, padx=5, pady=5)

        # Кнопка добавления
        ttk.Button(root, text="Добавить расход", command=self.add_expense).grid(
            row=3, column=0, columnspan=2, pady=10)

        # Таблица расходов
        self.tree = ttk.Treeview(root, columns=("amount", "category", "date"), show='headings')
        self.tree.heading("amount", text="Сумма", anchor="center")
        self.tree.heading("category", text="Категория", anchor="center")
        self.tree.heading("date", text="Дата", anchor="center")
        self.tree.column("amount", width=100)
        self.tree.column("category", width=200)
        self.tree.column("date", width=120)
        self.tree.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        # Фильтрация и подсчёт суммы
        ttk.Label(root, text="Фильтр по категории:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.filter_category_entry = ttk.Entry(root)
        self.filter_category_entry.grid(row=5, column=1, padx=5, pady=5)

        ttk.Label(root, text="Период (с - по):").grid(row=6, column=0, padx=5, pady=5, sticky="e")
        self.start_date_entry = ttk.Entry(root)
        self.start_date_entry.grid(row=6, column=1, padx=(0, 2), pady=5)
        
        self.end_date_entry = ttk.Entry(root)
        self.end_date_entry.grid(row=6, column=1, padx=(200, 0), pady=5) # Сдвиг для второго поля

        ttk.Button(root, text="Фильтровать/Подсчитать", command=self.filter_and_sum).grid(
            row=7, column=0, columnspan=2, pady=10)

        self.sum_label = ttk.Label(root, text="Сумма: 0.00 ₽", font=('Arial', 12))
        self.sum_label.grid(row=8, column=0, columnspan=2)

        # Настройка сетки для растягивания таблицы
        root.grid_rowconfigure(4, weight=1)
        root.grid_columnconfigure(1, weight=1)

    # --- МЕТОДЫ ЛОГИКИ ---
    def add_expense(self):
        amount = self.amount_entry.get()
        category = self.category_entry.get()
        date = self.date_entry.get()

        if not self.validate_input(amount, date):
            return

        expense = {
            "amount": float(amount),
            "category": category,
            "date": date
        }

        self.expenses.append(expense)
        self.save_data()
        self.update_table()
        
    def validate_input(self, amount_str: str, date_str: str) -> bool:
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Сумма должна быть больше нуля.")
            datetime.strptime(date_str.strip(), "%Y-%m-%d")
            return True
        except ValueError as e:
            error_text = str(e) if str(e) else "Неверный формат данных. Сумма > 0. Дата: ГГГГ-ММ-ДД."
            messagebox.showerror("Ошибка ввода", error_text)
            return False

    def filter_and_sum(self):
        category_filter = self.filter_category_entry.get().strip().lower()
        
        try:
            start_date = datetime.strptime(self.start_date_entry.get().strip(), "%Y-%m-%d").date() \
                if self.start_date_entry.get().strip() else None
            end_date = datetime.strptime(self.end_date_entry.get().strip(), "%Y-%m-%d").date() \
                if self.end_date_entry.get().strip() else None
            
            if (self.start_date_entry.get().strip() and not start_date) or \
               (self.end_date_entry.get().strip() and not end_date):
                raise ValueError

            filtered = self.expenses.copy()
            
            if category_filter:
                filtered = [e for e in filtered if e["category"].lower() == category_filter]
                
            if start_date:
                filtered = [e for e in filtered if datetime.strptime(e["date"], "%Y-%m-%d").date() >= start_date]
                
            if end_date:
                filtered = [e for e in filtered if datetime.strptime(e["date"], "%Y-%m-%d").date() <= end_date]
                
            total_sum = sum(e["amount"] for e in filtered)
            self.sum_label.config(text=f"Сумма: {total_sum:.2f} ₽")
            self.update_table(filtered)
            
            return

        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД.")

    # --- МЕТОДЫ РАБОТЫ С ДАННЫМИ ---
    def update_table(self, data=None):
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        display_data = data if data is not None else self.expenses
            
        for expense in display_data:
            # Округляем сумму до 2 знаков после запятой для красоты вывода
            amount_display = f"{expense['amount']:.2f}"
            self.tree.insert("", "end", values=(amount_display,
                                                expense["category"],
                                                expense["date"]))
    
    def save_data(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        with open(self.data_file, "w") as f:
            json.dump(self.expenses, f, indent=4)
    
    def load_data(self):
         try:
             with open(self.data_file, "r") as f:
                 self.expenses = json.load(f)
         except (FileNotFoundError, json.JSONDecodeError):
             self.expenses = []
             # Если файл не найден или пустой — просто работаем с пустым списком

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()