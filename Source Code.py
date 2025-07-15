import tkinter as tk
from tkinter import ttk
import webbrowser
import os
import webview
from tkinter import messagebox
import requests
from bs4 import BeautifulSoup

def get_topics(class_folder, subfolder):
    folder_path = os.path.join(class_folder, subfolder)
    if not os.path.isdir(folder_path):
        return []
    return [os.path.splitext(f)[0] for f in os.listdir(folder_path) if f.endswith('.txt')]

def load_notes(class_folder, topic):
    notes = []
    notes_file = os.path.join(class_folder, "notes", f"{topic}.txt")
    try:
        with open(notes_file, 'r', encoding='utf-8') as f:
            for line in f:
                note = line.strip()
                if note:
                    notes.append(note)
    except FileNotFoundError:
        pass
    return notes

def load_videos(class_folder, topic):
    pass  # No longer used

class TheStudyHacket(tk.Tk):
    def update_content(self):
        class_folder = self.class_var.get()
        subject = self.subject_var.get()
        self.notes_list.delete(0, tk.END)

        notes_folder = os.path.join(class_folder, "notes", subject)
        if os.path.isdir(notes_folder):
            for f in os.listdir(notes_folder):
                if f.lower().endswith('.pdf'):
                    self.notes_list.insert(tk.END, os.path.join(notes_folder, f))

    def update_subjects(self):
        class_folder = self.class_var.get()
        notes_path = os.path.join(class_folder, "notes")
        subjects = [f for f in os.listdir(notes_path) if os.path.isdir(os.path.join(notes_path, f))] if os.path.isdir(notes_path) else []
        subjects = sorted(subjects)
        self.subject_menu['values'] = subjects
        if subjects:
            self.subject_var.set(subjects[0])
        else:
            self.subject_var.set('')
        self.update_content()
    def open_note(self, event):
        selection = self.notes_list.curselection()
        if selection:
            pdf_path = self.notes_list.get(selection[0])
            try:
                os.startfile(pdf_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open PDF: {e}")

    def __init__(self):
        super().__init__()
        self.title("The Study Hacket")
        self.geometry("900x700")
        self.configure(bg="#0a0a23")  # Sci-fi black background
        self.class_choices = ["class9", "class10"]
        self.create_widgets()

    def create_widgets(self):
        sci_fi_font = ("Consolas", 12, "bold")
        label_fg = "#00bfff"  # Neon blue
        widget_bg = "#0a0a23"
        widget_fg = "#00bfff"
        listbox_bg = "#1a1a2e"
        listbox_fg = "#00bfff"
        highlight_bg = "#003366"

        tk.Label(self, text="Select Class:", font=sci_fi_font, fg=label_fg, bg=widget_bg).pack(pady=10)
        self.class_var = tk.StringVar(value=self.class_choices[0])
        class_menu = ttk.Combobox(self, textvariable=self.class_var, values=self.class_choices, state="readonly", font=sci_fi_font)
        class_menu.pack()
        class_menu.bind("<<ComboboxSelected>>", lambda e: self.update_subjects())
        class_menu.configure(background=widget_bg, foreground=widget_fg)

        tk.Label(self, text="Select Subject:", font=sci_fi_font, fg=label_fg, bg=widget_bg).pack(pady=10)
        self.subject_var = tk.StringVar()
        self.subject_menu = ttk.Combobox(self, textvariable=self.subject_var, state="readonly", font=sci_fi_font)
        self.subject_menu.pack()
        self.subject_menu.configure(background=widget_bg, foreground=widget_fg)
        self.subject_menu.bind("<<ComboboxSelected>>", lambda e: self.update_content())

        self.notes_label = tk.Label(self, text="Notes:", font=("Consolas", 12, "bold"), fg=label_fg, bg=widget_bg)
        self.notes_label.pack(pady=(20, 0))
        self.notes_list = tk.Listbox(self, width=70, height=20, bg=listbox_bg, fg=listbox_fg, font=("Consolas", 11), selectbackground=highlight_bg, selectforeground=widget_fg)
        self.notes_list.pack()
        self.notes_list.bind("<Double-Button-1>", self.open_note)

        self.update_subjects()

    # Removed video logic and Brave browser detection as only notes (PDFs) are supported

if __name__ == "__main__":
    app = TheStudyHacket()
    app.mainloop()
