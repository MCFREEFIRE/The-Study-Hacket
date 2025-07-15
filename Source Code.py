import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk
import fitz  # PyMuPDF
import threading
import time


class SplashScreen(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.overrideredirect(True)
        self.configure(bg="#0a0a23")
        self.geometry("400x300+500+200")

        try:
            title_font = ("Algerian", 28)
        except:
            title_font = ("Consolas", 24)

        tk.Label(self, text="The Study Hacket", font=title_font, fg="#00bfff", bg="#0a0a23").pack(pady=60)
        self.loading_label = tk.Label(self, text="Loading", font=("Consolas", 14), fg="#00bfff", bg="#0a0a23")
        self.loading_label.pack()

        self.animate_loading()

    def animate_loading(self):
        def run():
            dots = 0
            while True:
                if not self.winfo_exists():
                    break
                self.loading_label.config(text="Loading" + "." * dots)
                dots = (dots + 1) % 4
                time.sleep(0.5)
        threading.Thread(target=run, daemon=True).start()


class TheStudyHacket(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()  # Hide main window initially
        self.after(3000, self.show_main_app)  # Wait 3 seconds before showing main app

        self.splash = SplashScreen(self)

    def show_main_app(self):
        self.splash.destroy()
        self.deiconify()
        self.title("The Study Hacket")
        self.geometry("900x700")
        self.configure(bg="#0a0a23")
        self.class_choices = ["class9", "class10"]
        self.create_widgets()

    def create_widgets(self):
        sci_fi_font = ("Consolas", 12, "bold")
        label_fg = "#00bfff"
        widget_bg = "#0a0a23"
        widget_fg = "#00bfff"
        listbox_bg = "#1a1a2e"
        listbox_fg = "#00bfff"
        highlight_bg = "#003366"

        try:
            title_font = ("Algerian", 28)
        except:
            title_font = ("Consolas", 24)
        tk.Label(self, text="The Study Hacket", font=title_font, fg=label_fg, bg=widget_bg).pack(pady=20)

        tk.Label(self, text="Select Class:", font=sci_fi_font, fg=label_fg, bg=widget_bg).pack(pady=10)
        self.class_var = tk.StringVar(value=self.class_choices[0])
        class_menu = ttk.Combobox(self, textvariable=self.class_var, values=self.class_choices, state="readonly", font=sci_fi_font)
        class_menu.pack()
        class_menu.bind("<<ComboboxSelected>>", lambda e: self.update_subjects())

        tk.Label(self, text="Select Subject:", font=sci_fi_font, fg=label_fg, bg=widget_bg).pack(pady=10)
        self.subject_var = tk.StringVar()
        self.subject_menu = ttk.Combobox(self, textvariable=self.subject_var, state="readonly", font=sci_fi_font)
        self.subject_menu.pack()
        self.subject_menu.bind("<<ComboboxSelected>>", lambda e: self.update_content())

        self.notes_label = tk.Label(self, text="Notes:", font=sci_fi_font, fg=label_fg, bg=widget_bg)
        self.notes_label.pack(pady=(20, 0))
        self.notes_list = tk.Listbox(self, width=70, height=20, bg=listbox_bg, fg=listbox_fg,
                                     font=("Consolas", 11), selectbackground=highlight_bg, selectforeground=widget_fg)
        self.notes_list.pack()
        self.notes_list.bind("<Double-Button-1>", self.open_note)

        tk.Button(self, text="❌ Close App", command=self.destroy, font=sci_fi_font,
                  bg="#1a1a2e", fg="red", activebackground="#330000").pack(pady=10)

        self.update_subjects()

    def update_subjects(self):
        class_folder = self.class_var.get()
        notes_path = os.path.join(class_folder, "notes")
        subjects = [f for f in os.listdir(notes_path) if os.path.isdir(os.path.join(notes_path, f))] if os.path.isdir(notes_path) else []
        self.subject_menu['values'] = sorted(subjects)
        if subjects:
            self.subject_var.set(subjects[0])
        else:
            self.subject_var.set('')
        self.update_content()

    def update_content(self):
        class_folder = self.class_var.get()
        subject = self.subject_var.get()
        self.notes_list.delete(0, tk.END)
        notes_folder = os.path.join(class_folder, "notes", subject)
        if os.path.isdir(notes_folder):
            for f in os.listdir(notes_folder):
                if f.lower().endswith('.pdf'):
                    self.notes_list.insert(tk.END, os.path.join(notes_folder, f))

    def open_note(self, event):
        selection = self.notes_list.curselection()
        if selection:
            pdf_path = self.notes_list.get(selection[0])
            try:
                self.show_pdf_viewer(pdf_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open PDF: {e}")

    def show_pdf_viewer(self, pdf_path):
        pdf_win = tk.Toplevel(self)
        pdf_win.title(os.path.basename(pdf_path))
        pdf_win.geometry("600x750")
        pdf_win.configure(bg="#0a0a23")

        canvas = tk.Canvas(pdf_win, bg="#0a0a23", highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        current_page = [0]

        def render_page():
            page = doc.load_page(current_page[0])
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img.thumbnail((580, 720))
            photo = ImageTk.PhotoImage(img)
            canvas.delete("all")
            canvas.create_image(10, 10, anchor="nw", image=photo)
            canvas.image = photo
            page_label.config(text=f"Page {current_page[0] + 1} of {total_pages}")

        def next_page():
            if current_page[0] < total_pages - 1:
                current_page[0] += 1
                render_page()

        def prev_page():
            if current_page[0] > 0:
                current_page[0] -= 1
                render_page()

        nav_frame = tk.Frame(pdf_win, bg="#0a0a23")
        nav_frame.pack(pady=10)

        prev_btn = tk.Button(nav_frame, text="⏮ Previous", command=prev_page, bg="#1a1a2e", fg="white", font=("Consolas", 10))
        prev_btn.pack(side="left", padx=10)

        page_label = tk.Label(nav_frame, text="", fg="#00bfff", bg="#0a0a23", font=("Consolas", 10))
        page_label.pack(side="left")

        next_btn = tk.Button(nav_frame, text="Next ⏭", command=next_page, bg="#1a1a2e", fg="white", font=("Consolas", 10))
        next_btn.pack(side="left", padx=10)

        tk.Button(pdf_win, text="⬅ Back to Home", command=pdf_win.destroy,
                  bg="#333333", fg="white", font=("Consolas", 10)).pack(pady=10)

        render_page()


if __name__ == "__main__":
    app = TheStudyHacket()
    app.mainloop()
