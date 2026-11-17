
import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

# ---------------- DATABASE ----------------

conn = sqlite3.connect("contacts.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT,
    address TEXT
)
""")

conn.commit()

selected_contact_id = None

# ---------------- MAIN WINDOW ----------------

root = tk.Tk()
root.title("Contact Book")
root.geometry("850x700")
root.configure(bg="#EEF4FF")
root.resizable(True, True)


# ---------------- HEADING ----------------

title = tk.Label(
    root,
    text="CONTACT BOOK",
    font=("Arial", 27, "bold"),
    bg="#EEF4FF",
    fg="#1565C0"
)
title.pack(pady=20)

subtitle = tk.Label(
    root,
    text="Manage Your Contacts Easily",
    font=("Arial", 12),
    bg="#EEF4FF",
    fg="#555555"
)
subtitle.pack()


# ---------------- INPUT FIELDS ----------------

frame = tk.Frame(root, bg="#EEF4FF")
frame.pack(pady=15)


def create_field(label, row):
    tk.Label(
        frame,
        text=label,
        font=("Arial", 12),
        bg="#EEF4FF"
    ).grid(row=row, column=0, padx=15, pady=8, sticky="w")

    entry = tk.Entry(frame, font=("Arial", 12), width=32)
    entry.grid(row=row, column=1, pady=8)

    return entry


name_entry = create_field("Name:", 0)
phone_entry = create_field("Phone:", 1)
email_entry = create_field("Email:", 2)
address_entry = create_field("Address:", 3)


# ---------------- CLEAR FIELDS ----------------

def clear_fields():
    global selected_contact_id

    name_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)
    address_entry.delete(0, tk.END)

    selected_contact_id = None


# ---------------- ADD CONTACT ----------------

def add_contact():

    name = name_entry.get().strip()
    phone = phone_entry.get().strip()
    email = email_entry.get().strip()
    address = address_entry.get().strip()

    if not name or not phone:
        messagebox.showwarning(
            "Warning",
            "Name and Phone are required!"
        )
        return

    try:
        cursor.execute("""
            INSERT INTO contacts (name, phone, email, address)
            VALUES (?, ?, ?, ?)
        """, (name, phone, email, address))

        conn.commit()

        messagebox.showinfo(
            "Success",
            "Contact added successfully!"
        )

        clear_fields()

    except sqlite3.Error as error:
        messagebox.showerror("Database Error", str(error))


# ---------------- DISPLAY CONTACTS ----------------

def display_contacts(records, window_title):

    view_window = tk.Toplevel(root)
    view_window.title(window_title)
    view_window.geometry("950x480")
    view_window.configure(bg="#EEF4FF")

    heading = tk.Label(
        view_window,
        text=window_title.upper(),
        font=("Arial", 20, "bold"),
        bg="#EEF4FF",
        fg="#1565C0"
    )
    heading.pack(pady=15)

    table_frame = tk.Frame(view_window)
    table_frame.pack(fill="both", expand=True, padx=15, pady=10)

    columns = ("ID", "Name", "Phone", "Email", "Address")

    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        selectmode="browse"
    )

    for col in columns:
        tree.heading(col, text=col)

    tree.column("ID", width=50, anchor="center")
    tree.column("Name", width=150)
    tree.column("Phone", width=120)
    tree.column("Email", width=220)
    tree.column("Address", width=200)

    scroll = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=tree.yview
    )

    tree.configure(yscrollcommand=scroll.set)

    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    for record in records:
        tree.insert("", tk.END, values=record)

    if not records:
        tk.Label(
            view_window,
            text="No contacts found!",
            font=("Arial", 12),
            bg="#EEF4FF",
            fg="red"
        ).pack(pady=5)

    def load_selected_contact():

        global selected_contact_id

        selected = tree.selection()

        if not selected:
            messagebox.showwarning(
                "Warning",
                "Please select a contact first!",
                parent=view_window
            )
            return

        values = tree.item(selected[0], "values")

        selected_contact_id = int(values[0])

        name_entry.delete(0, tk.END)
        phone_entry.delete(0, tk.END)
        email_entry.delete(0, tk.END)
        address_entry.delete(0, tk.END)

        name_entry.insert(0, values[1])
        phone_entry.insert(0, values[2])
        email_entry.insert(0, values[3])
        address_entry.insert(0, values[4])

        view_window.destroy()

        messagebox.showinfo(
            "Contact Selected",
            "Contact loaded successfully!\nYou can now edit the details."
        )

    button_frame = tk.Frame(view_window, bg="#EEF4FF")
    button_frame.pack(pady=12)

    tk.Button(
        button_frame,
        text="Select Contact",
        font=("Arial", 11, "bold"),
        bg="#198754",
        fg="white",
        width=18,
        command=load_selected_contact
    ).grid(row=0, column=0, padx=10)

    tk.Button(
        button_frame,
        text="Close",
        font=("Arial", 11, "bold"),
        bg="#1565C0",
        fg="white",
        width=15,
        command=view_window.destroy
    ).grid(row=0, column=1, padx=10)


# ---------------- VIEW CONTACTS ----------------

def view_contacts():

    cursor.execute(
        "SELECT * FROM contacts ORDER BY id DESC"
    )

    records = cursor.fetchall()

    display_contacts(records, "Saved Contacts")


# ---------------- SEARCH CONTACT ----------------

def search_contact():

    search_text = search_entry.get().strip()

    if not search_text:
        messagebox.showwarning(
            "Warning",
            "Please enter a name or phone number!"
        )
        return

    cursor.execute("""
        SELECT * FROM contacts
        WHERE name LIKE ? OR phone LIKE ?
        ORDER BY id DESC
    """, (f"%{search_text}%", f"%{search_text}%"))

    records = cursor.fetchall()

    display_contacts(records, "Search Results")


# ---------------- UPDATE CONTACT ----------------

def update_contact():

    global selected_contact_id

    if selected_contact_id is None:
        messagebox.showwarning(
            "Warning",
            "First select a contact from View Contacts!"
        )
        return

    name = name_entry.get().strip()
    phone = phone_entry.get().strip()
    email = email_entry.get().strip()
    address = address_entry.get().strip()

    if not name or not phone:
        messagebox.showwarning(
            "Warning",
            "Name and Phone are required!"
        )
        return

    try:
        cursor.execute("""
            UPDATE contacts
            SET name = ?, phone = ?, email = ?, address = ?
            WHERE id = ?
        """, (
            name,
            phone,
            email,
            address,
            selected_contact_id
        ))

        if cursor.rowcount == 0:
            messagebox.showwarning(
                "Warning",
                "Contact not found. Please select again."
            )
            clear_fields()
            return

        conn.commit()

        messagebox.showinfo(
            "Success",
            "Contact updated successfully!"
        )

        clear_fields()

    except sqlite3.Error as error:
        messagebox.showerror("Database Error", str(error))


# ---------------- DELETE CONTACT ----------------

def delete_contact():

    delete_window = tk.Toplevel(root)
    delete_window.title("Delete Contact")
    delete_window.geometry("900x450")
    delete_window.configure(bg="#EEF4FF")

    heading = tk.Label(
        delete_window,
        text="DELETE CONTACT",
        font=("Arial", 20, "bold"),
        bg="#EEF4FF",
        fg="#D32F2F"
    )
    heading.pack(pady=15)

    table_frame = tk.Frame(delete_window)
    table_frame.pack(fill="both", expand=True, padx=15, pady=10)

    columns = ("ID", "Name", "Phone", "Email", "Address")

    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        selectmode="browse"
    )

    for col in columns:
        tree.heading(col, text=col)

    tree.column("ID", width=50, anchor="center")
    tree.column("Name", width=150)
    tree.column("Phone", width=120)
    tree.column("Email", width=200)
    tree.column("Address", width=200)

    scroll = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=tree.yview
    )

    tree.configure(yscrollcommand=scroll.set)

    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    cursor.execute("SELECT * FROM contacts ORDER BY id DESC")
    records = cursor.fetchall()

    for record in records:
        tree.insert("", tk.END, values=record)

    if not records:
        tk.Label(
            delete_window,
            text="No contacts available to delete!",
            font=("Arial", 12),
            bg="#EEF4FF",
            fg="red"
        ).pack(pady=5)

    def confirm_delete():

        selected = tree.selection()

        if not selected:
            messagebox.showwarning(
                "Warning",
                "Please select a contact to delete!",
                parent=delete_window
            )
            return

        values = tree.item(selected[0], "values")

        contact_id = int(values[0])
        contact_name = values[1]

        answer = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete {contact_name}?",
            parent=delete_window
        )

        if answer:

            try:
                cursor.execute(
                    "DELETE FROM contacts WHERE id = ?",
                    (contact_id,)
                )

                conn.commit()

                tree.delete(selected[0])

                messagebox.showinfo(
                    "Success",
                    "Contact deleted successfully!",
                    parent=delete_window
                )

            except sqlite3.Error as error:
                messagebox.showerror(
                    "Database Error",
                    str(error),
                    parent=delete_window
                )

    button_frame = tk.Frame(delete_window, bg="#EEF4FF")
    button_frame.pack(pady=12)

    tk.Button(
        button_frame,
        text="Delete Selected",
        font=("Arial", 11, "bold"),
        bg="#D32F2F",
        fg="white",
        width=18,
        command=confirm_delete
    ).grid(row=0, column=0, padx=10)

    tk.Button(
        button_frame,
        text="Close",
        font=("Arial", 11, "bold"),
        bg="#1565C0",
        fg="white",
        width=15,
        command=delete_window.destroy
    ).grid(row=0, column=1, padx=10)


# ---------------- SEARCH FRAME ----------------

search_frame = tk.Frame(root, bg="#EEF4FF")
search_frame.pack(pady=15)

search_entry = tk.Entry(
    search_frame,
    font=("Arial", 12),
    width=30
)
search_entry.grid(row=0, column=0, padx=10)

tk.Button(
    search_frame,
    text="Search Contact",
    font=("Arial", 11, "bold"),
    bg="#FF9800",
    fg="white",
    command=search_contact
).grid(row=0, column=1, padx=10)


# ---------------- BUTTON FRAME ----------------

button_frame = tk.Frame(root, bg="#EEF4FF")
button_frame.pack(pady=15)

tk.Button(
    button_frame,
    text="Add Contact",
    font=("Arial", 11, "bold"),
    bg="#1565C0",
    fg="white",
    width=18,
    command=add_contact
).grid(row=0, column=0, padx=8, pady=8)

tk.Button(
    button_frame,
    text="View Contacts",
    font=("Arial", 11, "bold"),
    bg="#198754",
    fg="white",
    width=18,
    command=view_contacts
).grid(row=0, column=1, padx=8, pady=8)

tk.Button(
    button_frame,
    text="Update Contact",
    font=("Arial", 11, "bold"),
    bg="#7B1FA2",
    fg="white",
    width=18,
    command=update_contact
).grid(row=1, column=0, padx=8, pady=8)

tk.Button(
    button_frame,
    text="Delete Contact",
    font=("Arial", 11, "bold"),
    bg="#D32F2F",
    fg="white",
    width=18,
    command=delete_contact
).grid(row=1, column=1, padx=8, pady=8)

tk.Button(
    button_frame,
    text="Clear Fields",
    font=("Arial", 11, "bold"),
    bg="#607D8B",
    fg="white",
    width=18,
    command=clear_fields
).grid(row=2, column=0, columnspan=2, pady=8)


# ---------------- CLOSE APPLICATION ----------------

def close_application():
    conn.close()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", close_application)

root.mainloop()
