import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3

# Connect to SQLite DB
conn = sqlite3.connect("listOfTasks.db")
cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT,
        due_date TEXT,
        done INTEGER DEFAULT 0
    )
""")
conn.commit()

# Global variable for theme mode
dark_mode = True

# Refresh task list
def list_update():
    task_listbox.delete(*task_listbox.get_children())
    cur.execute("SELECT id, title, category, due_date, done FROM tasks")
    for row in cur.fetchall():
        status = "✅" if row[4] else "❌"
        task_listbox.insert('', 'end', values=(row[0], row[1], row[2], row[3], status))

# Add task
def add_task():
    title = task_title.get().strip()
    category = task_category.get().strip()
    due = due_date.get()

    if not title:
        messagebox.showwarning("Input Error", "Task Title cannot be empty.")
        return

    cur.execute("INSERT INTO tasks (title, category, due_date) VALUES (?, ?, ?)", (title, category, due))
    conn.commit()
    list_update()
    task_title.delete(0, tk.END)

# Delete selected task
def delete_task():
    selected = task_listbox.selection()
    if not selected:
        messagebox.showinfo("Error", "No Task Selected.")
        return
    for item in selected:
        task_id = task_listbox.item(item)['values'][0]
        cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    list_update()

# Delete all tasks
def delete_all_tasks():
    if messagebox.askyesno("Delete All", "Are you sure?"):
        cur.execute("DELETE FROM tasks")
        conn.commit()
        list_update()

# Mark as done
def mark_done():
    selected = task_listbox.selection()
    if not selected:
        messagebox.showinfo("Info", "Select a task to mark done.")
        return
    for item in selected:
        task_id = task_listbox.item(item)['values'][0]
        cur.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
    conn.commit()
    list_update()

# Theme toggle
def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode
    apply_theme()

def apply_theme():
    if dark_mode:
        app.configure(bg="#1e1e1e")
        input_frame.configure(bg="#1e1e1e")
        btn_frame.configure(bg="#1e1e1e")
        theme_btn.configure(text="🌞 Light Mode")
        style.configure("Treeview", background="#2e2e2e", foreground="white",
                        fieldbackground="#2e2e2e", rowheight=28)
        style.map("Treeview", background=[("selected", "#444444")])
        for widget in input_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg="#1e1e1e", fg="white")
    else:
        app.configure(bg="#ffffff")
        input_frame.configure(bg="#ffffff")
        btn_frame.configure(bg="#ffffff")
        theme_btn.configure(text="🌙 Dark Mode")
        style.configure("Treeview", background="#f0f0f0", foreground="black",
                        fieldbackground="#f0f0f0", rowheight=28)
        style.map("Treeview", background=[("selected", "#dcdcdc")])
        for widget in input_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg="#ffffff", fg="black")

# GUI Setup
app = tk.Tk()
app.title("📝 To-Do List Manager")
app.geometry("850x520")
app.resizable(False, False)

style = ttk.Style(app)
style.theme_use("clam")

# Input Frame
input_frame = tk.Frame(app)
input_frame.pack(pady=10)

tk.Label(input_frame, text="Title:").grid(row=0, column=0, padx=5)
task_title = ttk.Entry(input_frame, width=30)
task_title.grid(row=0, column=1, padx=5)

tk.Label(input_frame, text="Category:").grid(row=0, column=2, padx=5)
task_category = ttk.Entry(input_frame, width=20)
task_category.grid(row=0, column=3, padx=5)

tk.Label(input_frame, text="Due Date:").grid(row=0, column=4, padx=5)
due_date = DateEntry(input_frame, width=12, date_pattern='yyyy-mm-dd')
due_date.grid(row=0, column=5, padx=5)

# Button Frame
btn_frame = tk.Frame(app)
btn_frame.pack(pady=10)

ttk.Button(btn_frame, text="➕ Add Task", command=add_task, width=20).grid(row=0, column=0, padx=10)
ttk.Button(btn_frame, text="✅ Mark Done", command=mark_done, width=20).grid(row=0, column=1, padx=10)
ttk.Button(btn_frame, text="❌ Delete Task", command=delete_task, width=20).grid(row=0, column=2, padx=10)
ttk.Button(btn_frame, text="🗑️ Delete All", command=delete_all_tasks, width=20).grid(row=0, column=3, padx=10)

# Theme Toggle Button
theme_btn = ttk.Button(app, text="🌞 Light Mode", command=toggle_theme)
theme_btn.pack(pady=10)

# Treeview Frame
tree_frame = tk.Frame(app)
tree_frame.pack(fill="both", expand=True)

columns = ("ID", "Title", "Category", "Due Date", "Status")
task_listbox = ttk.Treeview(tree_frame, columns=columns, show='headings', height=13)
for col in columns:
    task_listbox.heading(col, text=col)
    task_listbox.column(col, anchor="center", width=120 if col != "Title" else 220)
task_listbox.pack(fill="both", expand=True, padx=10, pady=10)

apply_theme()
list_update()
app.mainloop()
