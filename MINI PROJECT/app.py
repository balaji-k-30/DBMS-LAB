"""
Student Record Management System
Python + Tkinter + MySQL
Install dependency: pip install mysql-connector-python
Update DB_CONFIG below with your local MySQL credentials before running.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Balaji",  # Replace with your MySQL password
    "database": "student_db",
}

def connect_db():
    return mysql.connector.connect(**DB_CONFIG)

class StudentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Record Management System")
        self.root.geometry("900x600")
        self.root.minsize(780, 520)
        self.selected_id = None

        title = tk.Label(
            root, text="STUDENT RECORD MANAGEMENT SYSTEM",
            font=("Arial", 18, "bold"), pady=14
        )
        title.pack(fill="x")

        form = ttk.LabelFrame(root, text="Student Details", padding=12)
        form.pack(fill="x", padx=16, pady=8)

        ttk.Label(form, text="Student ID (for update/delete):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.id_entry = ttk.Entry(form, width=28)
        self.id_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(form, text="Name:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.name_entry = ttk.Entry(form, width=35)
        self.name_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(form, text="Email:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.email_entry = ttk.Entry(form, width=35)
        self.email_entry.grid(row=1, column=3, sticky="w", padx=5, pady=5)

        ttk.Label(form, text="Course:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.course_entry = ttk.Entry(form, width=35)
        self.course_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(form, text="Semester:").grid(row=2, column=2, sticky="w", padx=5, pady=5)
        self.semester_entry = ttk.Entry(form, width=35)
        self.semester_entry.grid(row=2, column=3, sticky="w", padx=5, pady=5)

        buttons = ttk.Frame(root, padding=8)
        buttons.pack(fill="x", padx=12)
        ttk.Button(buttons, text="Add Student", command=self.add_student).pack(side="left", padx=4)
        ttk.Button(buttons, text="View / Refresh", command=self.load_students).pack(side="left", padx=4)
        ttk.Button(buttons, text="Update Selected ID", command=self.update_student).pack(side="left", padx=4)
        ttk.Button(buttons, text="Delete Selected ID", command=self.delete_student).pack(side="left", padx=4)
        ttk.Button(buttons, text="Clear Form", command=self.clear_form).pack(side="left", padx=4)

        table_frame = ttk.LabelFrame(root, text="Saved Student Records", padding=8)
        table_frame.pack(fill="both", expand=True, padx=16, pady=8)

        columns = ("student_id", "name", "email", "course", "semester")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        headings = {
            "student_id": "ID", "name": "Name", "email": "Email",
            "course": "Course", "semester": "Semester"
        }
        widths = {"student_id": 60, "name": 180, "email": 250, "course": 150, "semester": 90}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center")
        yscroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        yscroll.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.status = tk.StringVar(value="Ready. Connect this app to your local MySQL database.")
        ttk.Label(root, textvariable=self.status, relief="sunken", anchor="w").pack(fill="x", side="bottom")

        self.load_students(show_errors=False)

    def db_operation(self, operation, show_error=True):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            result = operation(conn, cursor)
            return result
        except Error as exc:
            if show_error:
                messagebox.showerror(
                    "MySQL Connection / Database Error",
                    f"{exc}\n\nCheck that MySQL Server is running, student_db exists, "
                    "and DB_CONFIG has the correct username and password."
                )
            self.status.set("Database operation failed. Check MySQL settings.")
            return None
        finally:
            try:
                cursor.close()
                conn.close()
            except (UnboundLocalError, AttributeError):
                pass

    def add_student(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        course = self.course_entry.get().strip()
        semester_text = self.semester_entry.get().strip()

        if not name or not email or not course or not semester_text:
            messagebox.showwarning("Missing Information", "Please fill in Name, Email, Course, and Semester.")
            return
        try:
            semester = int(semester_text)
            if semester < 1 or semester > 12:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid Semester", "Semester must be a whole number from 1 to 12.")
            return

        def operation(conn, cursor):
            cursor.execute(
                "INSERT INTO students (name, email, course, semester) VALUES (%s, %s, %s, %s)",
                (name, email, course, semester)
            )
            conn.commit()
            return cursor.lastrowid

        new_id = self.db_operation(operation)
        if new_id is not None:
            messagebox.showinfo("Success", f"Student added successfully. Student ID: {new_id}")
            self.status.set(f"Inserted student record with ID {new_id}.")
            self.clear_form()
            self.load_students()

    def load_students(self, show_errors=True):
        def operation(conn, cursor):
            cursor.execute("SELECT student_id, name, email, course, semester FROM students ORDER BY student_id")
            return cursor.fetchall()

        rows = self.db_operation(operation, show_error=show_errors)
        if rows is None:
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert("", "end", values=row)
        self.status.set(f"Loaded {len(rows)} record(s) from MySQL.")

    def get_form_data(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        course = self.course_entry.get().strip()
        semester_text = self.semester_entry.get().strip()
        if not all([name, email, course, semester_text]):
            messagebox.showwarning("Missing Information", "Fill in all student fields before updating.")
            return None
        try:
            semester = int(semester_text)
            if semester < 1 or semester > 12:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid Semester", "Semester must be a whole number from 1 to 12.")
            return None
        return name, email, course, semester

    def get_id(self):
        value = self.id_entry.get().strip()
        if not value:
            messagebox.showwarning("Student ID Required", "Enter or select a Student ID first.")
            return None
        try:
            student_id = int(value)
            if student_id < 1:
                raise ValueError
            return student_id
        except ValueError:
            messagebox.showwarning("Invalid Student ID", "Student ID must be a positive whole number.")
            return None

    def update_student(self):
        student_id = self.get_id()
        if student_id is None:
            return
        data = self.get_form_data()
        if data is None:
            return

        def operation(conn, cursor):
            cursor.execute(
                "UPDATE students SET name=%s, email=%s, course=%s, semester=%s WHERE student_id=%s",
                (*data, student_id)
            )
            conn.commit()
            return cursor.rowcount

        changed = self.db_operation(operation)
        if changed is not None:
            if changed:
                messagebox.showinfo("Success", "Student record updated successfully.")
                self.status.set(f"Updated student ID {student_id}.")
                self.load_students()
            else:
                messagebox.showwarning("Not Found", "No record found for that ID, or the values were unchanged.")

    def delete_student(self):
        student_id = self.get_id()
        if student_id is None:
            return
        if not messagebox.askyesno("Confirm Delete", f"Delete student record ID {student_id}?"):
            return

        def operation(conn, cursor):
            cursor.execute("DELETE FROM students WHERE student_id=%s", (student_id,))
            conn.commit()
            return cursor.rowcount

        deleted = self.db_operation(operation)
        if deleted is not None:
            if deleted:
                messagebox.showinfo("Success", "Student record deleted successfully.")
                self.status.set(f"Deleted student ID {student_id}.")
                self.clear_form()
                self.load_students()
            else:
                messagebox.showwarning("Not Found", "No student exists with that ID.")

    def on_select(self, _event=None):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        self.clear_form()
        self.id_entry.insert(0, values[0])
        self.name_entry.insert(0, values[1])
        self.email_entry.insert(0, values[2])
        self.course_entry.insert(0, values[3])
        self.semester_entry.insert(0, values[4])

    def clear_form(self):
        for entry in (self.id_entry, self.name_entry, self.email_entry, self.course_entry, self.semester_entry):
            entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentApp(root)
    root.mainloop()
