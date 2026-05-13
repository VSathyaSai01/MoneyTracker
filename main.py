# main.py

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel

from kivy.uix.screenmanager import ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

import sqlite3
import os
from datetime import datetime


# ---------------- DATABASE ---------------- #

db_folder = r"C:\Personal Projects\MoneyTracker"

if not os.path.exists(db_folder):
    os.makedirs(db_folder)

db_path = os.path.join(
    db_folder,
    "money_tracker.db"
)

conn = sqlite3.connect(db_path)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS records (
    date TEXT PRIMARY KEY,
    status TEXT,
    amount REAL
)
""")

conn.commit()


# ---------------- DATE INPUT ---------------- #

class DateInput(MDTextField):

    def insert_text(
        self,
        substring,
        from_undo=False
    ):

        substring = ''.join(
            filter(str.isdigit, substring)
        )

        current = self.text.replace("-", "")

        if len(current) >= 8:
            return

        new_text = current + substring

        formatted = ""

        if len(new_text) > 0:
            formatted += new_text[:2]

        if len(new_text) > 2:
            formatted += "-" + new_text[2:4]

        if len(new_text) > 4:
            formatted += "-" + new_text[4:8]

        self.text = formatted

        self.cursor = (len(self.text), 0)


# ---------------- HOME SCREEN ---------------- #

class HomeScreen(MDScreen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        main = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=20
        )

        card = MDCard(
            orientation="vertical",
            padding=25,
            spacing=20,
            radius=[25],
            elevation=10
        )

        # Title
        title = MDLabel(
            text="Money Tracker",
            halign="center",
            font_style="H3"
        )

        card.add_widget(title)

        # Date
        today = datetime.now().strftime(
            "%d-%m-%Y"
        )

        date_label = MDLabel(
            text=f"Today: {today}",
            halign="center",
            theme_text_color="Secondary"
        )

        card.add_widget(date_label)

        # Amount
        self.amount_input = MDTextField(
            hint_text="Enter Amount",
            mode="rectangle",
            input_filter="float"
        )

        card.add_widget(self.amount_input)

        # Save Buttons
        btn_layout = BoxLayout(
            spacing=15,
            size_hint_y=None,
            height=50
        )

        received_btn = MDRaisedButton(
            text="Received",
            md_bg_color=(0,0.6,0,1)
        )

        missed_btn = MDRaisedButton(
            text="Not Received",
            md_bg_color=(0.7,0,0,1)
        )

        received_btn.bind(
            on_press=self.received_money
        )

        missed_btn.bind(
            on_press=self.did_not_receive
        )

        btn_layout.add_widget(received_btn)
        btn_layout.add_widget(missed_btn)

        card.add_widget(btn_layout)

        # Search Title
        search_label = MDLabel(
            text="Search Records",
            halign="center",
            font_style="H5"
        )

        card.add_widget(search_label)

        # From Date
        self.from_input = DateInput(
            hint_text="From Date",
            mode="rectangle"
        )

        card.add_widget(self.from_input)

        # To Date
        self.to_input = DateInput(
            hint_text="To Date",
            mode="rectangle"
        )

        card.add_widget(self.to_input)

        # Search Button
        search_btn = MDRaisedButton(
            text="Search Records",
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.2,0.5,1,1)
        )

        search_btn.bind(
            on_press=self.search_records
        )

        card.add_widget(search_btn)

        # Message
        self.message_label = MDLabel(
            text="",
            halign="center"
        )

        card.add_widget(self.message_label)

        main.add_widget(card)

        self.add_widget(main)

    # Save Status
    def save_status(self, status):

        today = datetime.now().strftime(
            "%d-%m-%Y"
        )

        amount = (
            self.amount_input.text.strip()
        )

        if amount == "":

            self.message_label.text = (
                "Enter Amount"
            )

            return

        cursor.execute("""
        SELECT * FROM records
        WHERE date=?
        """, (today,))

        existing = cursor.fetchone()

        if existing:

            self.message_label.text = (
                "Today's entry already exists"
            )

            return

        cursor.execute("""
        INSERT INTO records
        VALUES (?, ?, ?)
        """, (
            today,
            status,
            float(amount)
        ))

        conn.commit()

        self.message_label.text = (
            "Saved Successfully"
        )

        self.amount_input.text = ""

    def received_money(self, instance):

        self.save_status("Received")

    def did_not_receive(self, instance):

        self.save_status("Not Received")

    # Search
    def search_records(self, instance):

        from_date = (
            self.from_input.text.strip()
        )

        to_date = (
            self.to_input.text.strip()
        )

        if from_date == "":

            self.message_label.text = (
                "Enter From Date"
            )

            return

        if to_date == "":

            to_date = datetime.now().strftime(
                "%d-%m-%Y"
            )

        results_screen = (
            self.manager.get_screen("results")
        )

        results_screen.load_results(
            from_date,
            to_date
        )

        self.manager.current = "results"


# ---------------- RESULTS SCREEN ---------------- #

class ResultsScreen(MDScreen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        main = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=20
        )

        # Title
        title = MDLabel(
            text="Search Results",
            halign="center",
            font_style="H4",
            size_hint_y=None,
            height=50
        )

        main.add_widget(title)

        # Edit Amount
        self.edit_amount_input = MDTextField(
            hint_text="Edit Amount",
            mode="rectangle",
            input_filter="float"
        )

        main.add_widget(self.edit_amount_input)

        # Update Buttons
        update_layout = BoxLayout(
            spacing=15,
            size_hint_y=None,
            height=50
        )

        update_received_btn = MDRaisedButton(
            text="Update as Received",
            md_bg_color=(0,0.6,0,1)
        )

        update_missed_btn = MDRaisedButton(
            text="Update as Not Received",
            md_bg_color=(0.7,0,0,1)
        )

        update_received_btn.bind(
            on_press=lambda x:
            self.update_record("Received")
        )

        update_missed_btn.bind(
            on_press=lambda x:
            self.update_record("Not Received")
        )

        update_layout.add_widget(update_received_btn)
        update_layout.add_widget(update_missed_btn)

        main.add_widget(update_layout)

        # Scroll Area
        self.scroll = ScrollView()

        self.results_layout = GridLayout(
            cols=1,
            spacing=15,
            size_hint_y=None,
            padding=10
        )

        self.results_layout.bind(
            minimum_height=self.results_layout.setter(
                "height"
            )
        )

        self.scroll.add_widget(
            self.results_layout
        )

        main.add_widget(self.scroll)

        # Back Button
        back_btn = MDRaisedButton(
            text="Back",
            pos_hint={"center_x":0.5},
            md_bg_color=(0.3,0.3,0.3,1)
        )

        back_btn.bind(
            on_press=self.go_back
        )

        main.add_widget(back_btn)

        self.add_widget(main)

    # Load Results
    def load_results(self, from_date, to_date):

        self.current_from_date = from_date
        self.current_to_date = to_date

        self.results_layout.clear_widgets()

        try:

            cursor.execute("""
            SELECT * FROM records
            """)

            data = cursor.fetchall()

            received_count = 0
            missed_count = 0
            total_amount = 0

            from_d = datetime.strptime(
                from_date,
                "%d-%m-%Y"
            )

            to_d = datetime.strptime(
                to_date,
                "%d-%m-%Y"
            )

            for row in data:

                date, status, amount = row

                db_date = datetime.strptime(
                    date,
                    "%d-%m-%Y"
                )

                if from_d <= db_date <= to_d:

                    total_amount += amount

                    if status == "Received":
                        received_count += 1
                    else:
                        missed_count += 1

                    card = MDCard(
                        orientation="horizontal",
                        padding=15,
                        spacing=15,
                        size_hint_y=None,
                        height=90,
                        radius=[20],
                        elevation=8
                    )

                    label = MDLabel(
                        text=f"{date}\n{status} | ₹{amount}",
                        theme_text_color="Primary"
                    )

                    edit_btn = MDRaisedButton(
                        text="Edit",
                        md_bg_color=(0.2,0.5,1,1)
                    )

                    edit_btn.bind(
                        on_press=lambda x,
                        d=date,
                        a=amount:
                        self.load_edit_record(
                            d,
                            a
                        )
                    )

                    card.add_widget(label)
                    card.add_widget(edit_btn)

                    self.results_layout.add_widget(
                        card
                    )

            # Summary
            self.results_layout.add_widget(
                MDLabel(
                    text=f"Received Days: {received_count}",
                    halign="center",
                    theme_text_color="Custom",
                    text_color=(0,1,0,1),
                    size_hint_y=None,
                    height=40
                )
            )

            self.results_layout.add_widget(
                MDLabel(
                    text=f"Missed Days: {missed_count}",
                    halign="center",
                    theme_text_color="Custom",
                    text_color=(1,0,0,1),
                    size_hint_y=None,
                    height=40
                )
            )

            self.results_layout.add_widget(
                MDLabel(
                    text=f"Total Amount: ₹{total_amount}",
                    halign="center",
                    theme_text_color="Custom",
                    text_color=(0.2,0.6,1,1),
                    size_hint_y=None,
                    height=40
                )
            )

        except Exception:

            self.results_layout.add_widget(
                MDLabel(
                    text="Invalid Date Format",
                    halign="center"
                )
            )

    # Load Record For Editing
    def load_edit_record(
        self,
        date,
        amount
    ):

        self.current_edit_date = date

        self.edit_amount_input.text = str(amount)

    # Update Record
    def update_record(self, status):

        if not hasattr(
            self,
            "current_edit_date"
        ):

            return

        amount = (
            self.edit_amount_input.text.strip()
        )

        if amount == "":

            return

        cursor.execute("""
        UPDATE records
        SET amount=?, status=?
        WHERE date=?
        """, (
            float(amount),
            status,
            self.current_edit_date
        ))

        conn.commit()

        # Reload Automatically
        self.load_results(
            self.current_from_date,
            self.current_to_date
        )

    # Back
    def go_back(self, instance):

        self.manager.current = "home"


# ---------------- APP ---------------- #

class MoneyTrackerApp(MDApp):

    def build(self):

        self.theme_cls.theme_style = "Dark"

        self.theme_cls.primary_palette = "Blue"

        sm = ScreenManager()

        sm.add_widget(
            HomeScreen(name="home")
        )

        sm.add_widget(
            ResultsScreen(name="results")
        )

        return sm


MoneyTrackerApp().run()