import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
import tkinter.simpledialog as simpledialog
import os
from datetime import datetime
import csv

FILENAME = "expenses.txt"

# ---------------------- Helper Functions ----------------------

def load_expenses():
    expenses = []
    if os.path.exists(FILENAME):
        with open(FILENAME, "r") as f:
            for idx, line in enumerate(f, start=1):
                parts = line.strip().split(",")
                if len(parts) == 3:
                    date, desc, amount = parts
                    expenses.append((idx, date, desc, amount))
    return expenses

def save_expense(date, desc, amount):
    with open(FILENAME, "a") as f:
        f.write(f"{date},{desc},{amount}\n")

def delete_expense_from_file(index):
    expenses = load_expenses()
    expenses = [exp for exp in expenses if exp[0] != index]
    with open(FILENAME, "w") as f:
        for i, date, desc, amount in expenses:
            f.write(f"{date},{desc},{amount}\n")

def edit_expense_in_file(index, new_date, new_desc, new_amount):
    expenses = load_expenses()
    new_expenses = []
    for i, date, desc, amount in expenses:
        if i == index:
            new_expenses.append((i, new_date, new_desc, new_amount))
        else:
            new_expenses.append((i, date, desc, amount))
    with open(FILENAME, "w") as f:
        for i, date, desc, amount in new_expenses:
            f.write(f"{date},{desc},{amount}\n")

# ---------------------- GUI Functions ----------------------

def refresh_tree():
    for row in tree.get_children():
        tree.delete(row)
    
    expenses = load_expenses()
    grouped = {}
    for idx, date, desc, amount in expenses:
        grouped.setdefault(date, []).append((idx, desc, amount))
    
    for date in sorted(grouped.keys()):
        parent = tree.insert("", "end", text=date, values=("", date, "", ""), open=False)
        for idx, desc, amount in grouped[date]:
            tree.insert(parent, "end", values=(idx, "", desc, f"{float(amount):.2f}"))

def add_expense_gui():
    date = simpledialog.askstring("Date", "Enter date (YYYY-MM-DD):")
    if not date:
        return
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Invalid Date", "Use format YYYY-MM-DD.")
        return
    
    desc = simpledialog.askstring("Description", "Enter description:")
    if not desc:
        return
    
    amount = simpledialog.askstring("Amount", "Enter amount:")
    try:
        float(amount)
    except ValueError:
        messagebox.showerror("Invalid Amount", "Amount must be a number.")
        return
    
    save_expense(date, desc, amount)
    refresh_tree()

def delete_expense_gui():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("No Selection", "Please select an expense to delete.")
        return
    item = selected[0]
    parent = tree.parent(item)
    if parent == "":
        messagebox.showinfo("Delete Group Not Allowed", "Please select an expense, not a date group.")
        return
    values = tree.item(item, "values")
    idx = values[0]
    if not idx:
        messagebox.showwarning("Invalid selection", "Cannot delete this item.")
        return
    idx = int(idx)
    
    if messagebox.askyesno("Confirm Delete", f"Delete expense: {values[2]} - {values[3]}?"):
        delete_expense_from_file(idx)
        refresh_tree()

def search_expense_gui():
    keyword = simpledialog.askstring("Search", "Enter date or keyword:").lower()
    if not keyword:
        return
    expenses = load_expenses()
    filtered = [exp for exp in expenses if keyword in exp[1].lower() or keyword in exp[2].lower()]
    for row in tree.get_children():
        tree.delete(row)
    grouped = {}
    for idx, date, desc, amount in filtered:
        grouped.setdefault(date, []).append((idx, desc, amount))
    for date in sorted(grouped.keys()):
        parent = tree.insert("", "end", text=date, values=("", date, "", ""), open=True)
        for idx, desc, amount in grouped[date]:
            tree.insert(parent, "end", values=(idx, "", desc, f"{float(amount):.2f}"))

def export_csv_gui():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return
    expenses = load_expenses()
    with open(file_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Index", "Date", "Description", "Amount"])
        writer.writerows(expenses)
    messagebox.showinfo("Export Complete", f"Expenses exported to {file_path}")

def edit_expense_gui():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("No Selection", "Please select an expense to edit.")
        return
    item = selected[0]
    parent = tree.parent(item)
    if parent == "":
        messagebox.showinfo("Edit Group Not Allowed", "Please select an expense, not a date group.")
        return
    values = tree.item(item, "values")
    idx = values[0]
    if not idx:
        messagebox.showwarning("Invalid selection", "Cannot edit this item.")
        return
    idx = int(idx)

    # Load current values
    curr_date = tree.item(parent, "text")
    curr_desc = values[2]
    curr_amount = values[3]

    # Edit dialogs
    new_date = simpledialog.askstring("Edit Date", "Enter date (YYYY-MM-DD):", initialvalue=curr_date)
    if not new_date:
        return
    try:
        datetime.strptime(new_date, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Invalid Date", "Use format YYYY-MM-DD.")
        return
    
    new_desc = simpledialog.askstring("Edit Description", "Enter description:", initialvalue=curr_desc)
    if not new_desc:
        return
    
    new_amount = simpledialog.askstring("Edit Amount", "Enter amount:", initialvalue=curr_amount)
    try:
        float(new_amount)
    except ValueError:
        messagebox.showerror("Invalid Amount", "Amount must be a number.")
        return

    edit_expense_in_file(idx, new_date, new_desc, new_amount)
    refresh_tree()

# ---------------------- Main Window ----------------------

root = tb.Window(themename="minty")
root.title("Expense Tracker")
root.geometry("750x550")

columns = ("ID", "Date", "Description", "Amount")
tree = tb.Treeview(root, columns=columns, show="headings", bootstyle="secondary")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center", stretch=True, width=150)
tree.pack(fill="both", expand=True, pady=10, padx=10)

btn_frame = tb.Frame(root)
btn_frame.pack(pady=5)

tb.Button(btn_frame, text="Add Expense", command=add_expense_gui, bootstyle="success").grid(row=0, column=0, padx=5)
tb.Button(btn_frame, text="Search", command=search_expense_gui, bootstyle="info").grid(row=0, column=1, padx=5)
tb.Button(btn_frame, text="Edit", command=edit_expense_gui, bootstyle="warning").grid(row=0, column=2, padx=5)
tb.Button(btn_frame, text="Delete", command=delete_expense_gui, bootstyle="danger").grid(row=0, column=3, padx=5)
tb.Button(btn_frame, text="Export CSV", command=export_csv_gui, bootstyle="primary").grid(row=0, column=4, padx=5)
tb.Button(btn_frame, text="Refresh", command=refresh_tree, bootstyle="secondary").grid(row=0, column=5, padx=5)

refresh_tree()
root.mainloop()
