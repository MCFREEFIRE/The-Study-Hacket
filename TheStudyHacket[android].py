from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivymd.uix.button import MDRaisedButton
from kivymd.app import MDApp
from kivy.core.window import Window
import os
import fitz  # PyMuPDF
from PIL import Image as PILImage

# Optional: fix window size for desktop testing
Window.size = (360, 640)

KV = '''
ScreenManager:
    SplashScreen:
    MainScreen:
    TopicsScreen:
    PDFViewer:

<SplashScreen>:
    name: 'splash'
    canvas.before:
        Color:
            rgba: 0.04, 0.04, 0.14, 1
        Rectangle:
            pos: self.pos
            size: self.size
    MDLabel:
        text: "The Study Hacket"
        halign: 'center'
        font_style: 'H4'
        theme_text_color: "Custom"
        text_color: 0, 0.75, 1, 1
        pos_hint: {"center_y": 0.7}
    MDLabel:
        id: loading_label
        text: "Loading"
        halign: 'center'
        theme_text_color: "Custom"
        text_color: 0, 0.75, 1, 1
        pos_hint: {"center_y": 0.6}

<MainScreen>:
    name: 'main'
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        canvas.before:
            Color:
                rgba: 0.04, 0.04, 0.14, 1
            Rectangle:
                pos: self.pos
                size: self.size

        MDLabel:
            text: "Select Your Class"
            font_style: 'H5'
            halign: 'center'
            theme_text_color: "Custom"
            text_color: 0, 0.75, 1, 1

        Spinner:
            id: class_spinner
            text: 'class9'
            values: ['class9', 'class10']
            size_hint_y: None
            height: dp(40)

        Spinner:
            id: subject_spinner
            text: ''
            values: []
            size_hint_y: None
            height: dp(40)

        MDRaisedButton:
            text: "Show Topics"
            md_bg_color: 0, 0.47, 0.8, 1
            on_release: root.go_to_topics()

        MDRaisedButton:
            text: "Close"
            md_bg_color: 1, 0, 0, 1
            on_release: app.stop()

<TopicsScreen>:
    name: 'topics'
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        canvas.before:
            Color:
                rgba: 0.04, 0.04, 0.14, 1
            Rectangle:
                pos: self.pos
                size: self.size

        MDLabel:
            id: header
            text: "Available Topics"
            font_style: 'H6'
            halign: 'center'
            theme_text_color: "Custom"
            text_color: 0, 0.75, 1, 1

        ScrollView:
            GridLayout:
                id: notes_grid
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                spacing: 5
                padding: 5

        MDRaisedButton:
            text: "Back"
            on_release: root.manager.current = 'main'
            md_bg_color: 0.2, 0.2, 0.4, 1

<PDFViewer>:
    name: 'viewer'
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: 0.04, 0.04, 0.14, 1
            Rectangle:
                pos: self.pos
                size: self.size

        Image:
            id: pdf_image
            allow_stretch: True
            keep_ratio: True

        BoxLayout:
            size_hint_y: None
            height: dp(50)
            spacing: 10
            padding: 5
            MDRaisedButton:
                text: "Previous"
                on_release: root.prev_page()
            MDLabel:
                id: page_label
                halign: 'center'
                theme_text_color: "Custom"
                text_color: 0, 0.75, 1, 1
            MDRaisedButton:
                text: "Next"
                on_release: root.next_page()

        MDRaisedButton:
            text: "Back to Topics"
            on_release: root.manager.current = 'topics'
            md_bg_color: 0.2, 0.2, 0.4, 1
'''

class SplashScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(self.start_animation, 0.1)
        Clock.schedule_once(self.goto_main, 3)

    def start_animation(self, dt):
        self.dots = 0
        self.label = self.ids.loading_label
        Clock.schedule_interval(self.animate_dots, 0.5)

    def animate_dots(self, dt):
        self.dots = (self.dots + 1) % 4
        self.label.text = "Loading" + "." * self.dots

    def goto_main(self, dt):
        self.manager.current = 'main'

class MainScreen(Screen):
    def on_enter(self):
        self.update_subjects()

    def update_subjects(self):
        class_folder = self.ids.class_spinner.text
        notes_path = os.path.join(class_folder, "notes")
        subjects = [f for f in os.listdir(notes_path) if os.path.isdir(os.path.join(notes_path, f))] if os.path.exists(notes_path) else []
        self.ids.subject_spinner.values = subjects
        if subjects:
            self.ids.subject_spinner.text = subjects[0]

    def go_to_topics(self):
        class_folder = self.ids.class_spinner.text
        subject = self.ids.subject_spinner.text
        notes_path = os.path.join(class_folder, "notes", subject)

        topic_screen = self.manager.get_screen('topics')
        topic_screen.load_notes(notes_path)
        topic_screen.ids.header.text = f"{subject.title()} Notes"
        self.manager.current = 'topics'

class TopicsScreen(Screen):
    def load_notes(self, path):
        self.ids.notes_grid.clear_widgets()
        if os.path.isdir(path):
            for f in os.listdir(path):
                if f.lower().endswith(".pdf"):
                    full_path = os.path.join(path, f)
                    btn = MDRaisedButton(
                        text=f,
                        size_hint_y=None,
                        height=40,
                        md_bg_color=(0.1, 0.2, 0.4, 1),
                        on_release=lambda x, p=full_path: self.open_pdf(p)
                    )
                    self.ids.notes_grid.add_widget(btn)

    def open_pdf(self, path):
        viewer = self.manager.get_screen('viewer')
        viewer.load_pdf(path)
        self.manager.current = 'viewer'

class PDFViewer(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pdf = None
        self.page_index = 0
        self.total_pages = 0

    def load_pdf(self, path):
        self.pdf = fitz.open(path)
        self.page_index = 0
        self.total_pages = len(self.pdf)
        self.render_page()

    def render_page(self):
        if not self.pdf:
            return

        page = self.pdf.load_page(self.page_index)
        pix = page.get_pixmap()
        img = PILImage.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img.thumbnail((360, 600))

        img_path = f"temp_page_{self.page_index}.png"
        img.save(img_path)

        # Force image reload
        self.ids.pdf_image.source = ''
        self.ids.pdf_image.source = img_path
        self.ids.pdf_image.reload()

        self.ids.page_label.text = f"Page {self.page_index + 1} of {self.total_pages}"

    def next_page(self):
        if self.page_index < self.total_pages - 1:
            self.page_index += 1
            self.render_page()

    def prev_page(self):
        if self.page_index > 0:
            self.page_index -= 1
            self.render_page()

class TheStudyHacketApp(MDApp):
    def build(self):
        self.title = "The Study Hacket"
        return Builder.load_string(KV)

if __name__ == '__main__':
    TheStudyHacketApp().run()
