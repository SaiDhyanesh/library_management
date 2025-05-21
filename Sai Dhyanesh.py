import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from datetime import datetime, timedelta

class Book:
    def __init__(self, book_id, title, author, copies):
        self.id = book_id
        self.title = title
        self.author = author
        self.total_copies = copies
        self.available_copies = copies

class Student:
    def __init__(self, name, student_id):
        self.name = name
        self.id = student_id
        self.issued_books = {}  # book_id: deadline

class Library:
    def __init__(self):
        self.books = {}         # book_id: Book
        self.students = {}      # student_id: Student

    def add_book(self, book_id, title, author, copies):
        if book_id in self.books:
            self.books[book_id].total_copies += copies
            self.books[book_id].available_copies += copies
        else:
            self.books[book_id] = Book(book_id, title, author, copies)

    def remove_book(self, book_id):
        if book_id in self.books and self.books[book_id].available_copies == self.books[book_id].total_copies:
            del self.books[book_id]
            return True
        return False

    def add_student(self, name, student_id):
        if student_id not in self.students:
            self.students[student_id] = Student(name, student_id)

    def issue_book(self, book_id, student_id, student_name):
        if book_id in self.books and self.books[book_id].available_copies > 0:
            self.add_student(student_name, student_id)
            self.books[book_id].available_copies -= 1
            deadline = datetime.now() + timedelta(days=14)
            self.students[student_id].issued_books[book_id] = deadline
            return True
        return False

    def return_book(self, book_id, student_id):
        if student_id in self.students and book_id in self.students[student_id].issued_books:
            del self.students[student_id].issued_books[book_id]
            self.books[book_id].available_copies += 1
            return True
        return False

    def extend_deadline(self, book_id, student_id, days):
        if student_id in self.students and book_id in self.students[student_id].issued_books:
            self.students[student_id].issued_books[book_id] += timedelta(days=days)
            return True
        return False

    def search_book(self, keyword):
        return [b for b in self.books.values() if keyword.lower() in b.title.lower() or keyword == b.id]

    def search_student(self, student_id):
        return self.students.get(student_id)

    def get_overdue_books(self):
        now = datetime.now()
        overdue = []
        for student in self.students.values():
            for book_id, deadline in student.issued_books.items():
                if deadline < now:
                    overdue.append((book_id, student.id, deadline))
        return overdue

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Login")
        self.root.geometry("300x200")

        tk.Label(root, text="Username:").pack(pady=5)
        self.username_entry = tk.Entry(root)
        self.username_entry.pack()

        tk.Label(root, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack()

        tk.Button(root, text="Login", command=self.check_login).pack(pady=10)

    def check_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username == "admin" and password == "admin123":
            self.root.destroy()
            main_root = tk.Tk()
            LibraryGUI(main_root)
            main_root.mainloop()
        else:
            messagebox.showerror("Error", "Invalid credentials")

class LibraryGUI:
    def __init__(self, root):
        self.library = Library()
        self.root = root
        self.root.title("📚 Library Management System")
        self.root.geometry("800x700")
        self.root.config(bg="#f0f0f0")

        title = tk.Label(root, text="Library Management System", font=("Helvetica", 18, "bold"), bg="#f0f0f0")
        title.pack(pady=20)

        buttons = [
            ("Add Book", self.add_book),
            ("Remove Book", self.remove_book),
            ("Show All Books", self.show_books),
            ("Issue Book", self.issue_book),
            ("Return Book", self.return_book),
            ("Show Student Details", self.show_student),
            ("Extend Deadline", self.extend_deadline),
            ("Search Book", self.search_book),
            ("Search Student", self.search_student),
            ("Show Overdue Books", self.show_overdue),
            ("Logout", self.logout)
        ]

        for text, cmd in buttons:
            tk.Button(root, text=text, command=cmd, font=("Arial", 12), width=30, bg="#4CAF50", fg="white").pack(pady=4)

    def add_book(self):
        def submit_book():
            book_id = id_entry.get()
            title = title_entry.get()
            author = author_entry.get()
            try:
                copies = int(copies_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Copies must be a number.")
                return

            if book_id and title and author and copies > 0:
                self.library.add_book(book_id, title, author, copies)
                messagebox.showinfo("Added", f"{copies} copy(ies) of '{title}' added.")
                add_another = messagebox.askyesno("Add Another", "Do you want to add another book?")
                if not add_another:
                    add_window.destroy()
                else:
                    id_entry.delete(0, tk.END)
                    title_entry.delete(0, tk.END)
                    author_entry.delete(0, tk.END)
                    copies_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "Please fill in all fields with valid values.")

        add_window = tk.Toplevel(self.root)
        add_window.title("Add Book")
        add_window.geometry("400x300")

        tk.Label(add_window, text="Book ID").pack()
        id_entry = tk.Entry(add_window)
        id_entry.pack()

        tk.Label(add_window, text="Title").pack()
        title_entry = tk.Entry(add_window)
        title_entry.pack()

        tk.Label(add_window, text="Author").pack()
        author_entry = tk.Entry(add_window)
        author_entry.pack()

        tk.Label(add_window, text="No. of Copies").pack()
        copies_entry = tk.Entry(add_window)
        copies_entry.pack()

        tk.Button(add_window, text="Add Book", command=submit_book).pack(pady=10)

    def remove_book(self):
        book_id = simpledialog.askstring("Remove Book", "Enter Book ID:")
        if book_id and self.library.remove_book(book_id):
            messagebox.showinfo("Removed", f"Book ID '{book_id}' removed.")
        else:
            messagebox.showerror("Error", "Book not found or some copies are issued.")

    def show_books(self):
        window = tk.Toplevel(self.root)
        window.title("All Books")
        cols = ("Book ID", "Title", "Author", "Total Copies", "Available Copies")
        tree = ttk.Treeview(window, columns=cols, show="headings")
        for col in cols:
            tree.heading(col, text=col)
        tree.pack(fill=tk.BOTH, expand=True)

        for b in self.library.books.values():
            tree.insert("", tk.END, values=(b.id, b.title, b.author, b.total_copies, b.available_copies))

    def issue_book(self):
        issue_window = tk.Toplevel(self.root)
        issue_window.title("Issue Book")
        issue_window.geometry("350x250")

        tk.Label(issue_window, text="Book ID:").pack()
        book_id_entry = tk.Entry(issue_window)
        book_id_entry.pack()

        tk.Label(issue_window, text="Student ID:").pack()
        student_id_entry = tk.Entry(issue_window)
        student_id_entry.pack()

        tk.Label(issue_window, text="Student Name:").pack()
        student_name_entry = tk.Entry(issue_window)
        student_name_entry.pack()

        def submit_issue():
            book_id = book_id_entry.get()
            student_id = student_id_entry.get()
            student_name = student_name_entry.get()
            if book_id and student_id and student_name:
                if self.library.issue_book(book_id, student_id, student_name):
                    messagebox.showinfo("Issued", f"Book '{book_id}' issued to student '{student_name}' ({student_id}).")
                    # Clear entries for next entry
                    book_id_entry.delete(0, tk.END)
                    student_id_entry.delete(0, tk.END)
                    student_name_entry.delete(0, tk.END)
                else:
                    messagebox.showerror("Error", "Book unavailable or invalid ID.")
            else:
                messagebox.showerror("Error", "Please fill all fields.")

        tk.Button(issue_window, text="Issue Book", command=submit_issue).pack(pady=10)

    def return_book(self):
        return_window = tk.Toplevel(self.root)
        return_window.title("Return Book")
        return_window.geometry("350x200")

        tk.Label(return_window, text="Book ID:").pack()
        book_id_entry = tk.Entry(return_window)
        book_id_entry.pack()

        tk.Label(return_window, text="Student ID:").pack()
        student_id_entry = tk.Entry(return_window)
        student_id_entry.pack()

        tk.Label(return_window, text="Student Name:").pack()
        student_name_entry = tk.Entry(return_window)
        student_name_entry.pack()

        def submit_return():
            book_id = book_id_entry.get()
            student_id = student_id_entry.get()
            student_name = student_name_entry.get()
            if book_id and student_id and student_name:
                if self.library.return_book(book_id, student_id):
                    messagebox.showinfo("Returned", f"Book '{book_id}' returned by student '{student_name}' ({student_id}).")
                    # Clear entries for next return
                    book_id_entry.delete(0, tk.END)
                    student_id_entry.delete(0, tk.END)
                    student_name_entry.delete(0, tk.END)
                else:
                    messagebox.showerror("Error", "No such issued book for this student.")
            else:
                messagebox.showerror("Error", "Please fill all fields.")

        tk.Button(return_window, text="Return Book", command=submit_return).pack(pady=10)

    def extend_deadline(self):
        extend_window = tk.Toplevel(self.root)
        extend_window.title("Extend Deadline")
        extend_window.geometry("350x220")

        tk.Label(extend_window, text="Book ID:").pack()
        book_id_entry = tk.Entry(extend_window)
        book_id_entry.pack()

        tk.Label(extend_window, text="Student ID:").pack()
        student_id_entry = tk.Entry(extend_window)
        student_id_entry.pack()

        tk.Label(extend_window, text="Extend by Days:").pack()
        days_entry = tk.Entry(extend_window)
        days_entry.pack()

        def submit_extend():
            book_id = book_id_entry.get()
            student_id = student_id_entry.get()
            try:
                days = int(days_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Days must be a number.")
                return

            if book_id and student_id and days > 0:
                if self.library.extend_deadline(book_id, student_id, days):
                    messagebox.showinfo("Extended", "Deadline extended.")
                    book_id_entry.delete(0, tk.END)
                    student_id_entry.delete(0, tk.END)
                    days_entry.delete(0, tk.END)
                else:
                    messagebox.showerror("Error", "Failed to extend deadline.")
            else:
                messagebox.showerror("Error", "Please fill all fields correctly.")

        tk.Button(extend_window, text="Extend Deadline", command=submit_extend).pack(pady=10)

    def show_student(self):
        window = tk.Toplevel(self.root)
        window.title("Student Details")
        cols = ("Student ID", "Name", "Book ID", "Deadline")
        tree = ttk.Treeview(window, columns=cols, show="headings")
        for col in cols:
            tree.heading(col, text=col)
        tree.pack(fill=tk.BOTH, expand=True)

        for student in self.library.students.values():
            for b_id, deadline in student.issued_books.items():
                tree.insert("", tk.END, values=(student.id, student.name, b_id, deadline.strftime('%Y-%m-%d')))

    def search_book(self):
        keyword = simpledialog.askstring("Search", "Enter Book Title or ID:")
        results = self.library.search_book(keyword)
        if results:
            msg = "\n".join([f"ID: {b.id}, Title: {b.title}, Author: {b.author}, Available: {b.available_copies}" for b in results])
            messagebox.showinfo("Search Results", msg)
        else:
            messagebox.showerror("Not Found", "No matching books.")

    def search_student(self):
        student_id = simpledialog.askstring("Search Student", "Enter Student ID:")
        student = self.library.search_student(student_id)
        if student:
            issued_books_info = "\n".join([f"{b_id} (Due: {deadline.strftime('%Y-%m-%d')})" for b_id, deadline in student.issued_books.items()]) or "No books issued."
            msg = f"Name: {student.name}, ID: {student.id}\nBooks Issued:\n{issued_books_info}"
            messagebox.showinfo("Student Found", msg)
        else:
            messagebox.showerror("Not Found", "Student not found.")

    def show_overdue(self):
        overdue = self.library.get_overdue_books()
        if overdue:
            msg = "\n".join([f"Book ID: {b}, Student ID: {s}, Due: {d.strftime('%Y-%m-%d')}" for b, s, d in overdue])
            messagebox.showinfo("Overdue Books", msg)
        else:
            messagebox.showinfo("None", "No overdue books.")

    def logout(self):
        self.root.destroy()
        login_root = tk.Tk()
        LoginWindow(login_root)
        login_root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()
