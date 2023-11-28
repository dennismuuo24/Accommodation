import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner  # Make sure to include this import
import mysql.connector
import re

kivy.require('1.11.1')

class DatabaseManager:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="dennis123",
            database="Accommodation"
        )
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.conn.close()

    def execute_query(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return False

    def fetch_data(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None


class LoginScreen(Screen):
    def __init__(self, db_manager, booking_form_screen, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.db_manager = db_manager
        self.booking_form_screen = booking_form_screen

        self.username_input = TextInput(hint_text='Username', multiline=False)
        self.password_input = TextInput(hint_text='Password', multiline=False, password=True)
        self.login_button = Button(text='Login', on_press=self.login)
        self.sign_up_button = Button(text='Sign Up', on_press=self.go_to_sign_up)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='Login Page'))
        layout.add_widget(self.username_input)
        layout.add_widget(self.password_input)
        layout.add_widget(self.login_button)
        layout.add_widget(self.sign_up_button)

        self.add_widget(layout)

    def login(self, instance):
        username = self.username_input.text
        password = self.password_input.text

        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        params = (username, password)

        result = self.db_manager.fetch_data(query, params)

        if result:
            self.show_popup("Login Successful", "User logged in successfully!")
            self.manager.current = 'booking_form'  # Set the current screen to 'booking_form'
        else:
            self.show_popup("Login Failed", "Invalid credentials!")

    def go_to_sign_up(self, instance):
        self.manager.current = 'sign_up'

    def show_popup(self, title, content):
        popup = Popup(title=title, content=Label(text=content), size_hint=(None, None), size=(400, 200))
        popup.open()


class SignUpScreen(Screen):
    def __init__(self, db_manager, login_screen, **kwargs):
        super(SignUpScreen, self).__init__(**kwargs)
        self.db_manager = db_manager
        self.login_screen = login_screen

        self.username_input = TextInput(hint_text='Username', multiline=False)
        self.password_input = TextInput(hint_text='Password', multiline=False, password=True)
        self.sign_up_button = Button(text='Sign Up', on_press=self.sign_up)
        self.back_to_login_button = Button(text='Back to Login', on_press=self.go_to_login)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='Sign Up Page'))
        layout.add_widget(self.username_input)
        layout.add_widget(self.password_input)
        layout.add_widget(self.sign_up_button)
        layout.add_widget(self.back_to_login_button)

        self.add_widget(layout)

    def sign_up(self, instance):
        username = self.username_input.text
        password = self.password_input.text

        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        params = (username, password)

        if self.db_manager.execute_query(query, params):
            self.show_popup("Sign Up Successful", "User registered successfully!")
            self.login_screen.current = 'login'
        else:
            self.show_popup("Sign Up Failed", "Failed to register user. Please try again.")

    def go_to_login(self, instance):
        self.manager.current = 'login'

    def show_popup(self, title, content):
        popup = Popup(title=title, content=Label(text=content), size_hint=(None, None), size=(400, 200))
        popup.open()


class BookingFormScreen(Screen):
    def __init__(self, db_manager, **kwargs):
        super(BookingFormScreen, self).__init__(**kwargs)
        self.db_manager = db_manager

        self.reg_number_input = TextInput(hint_text='Enter Reg Number (alphanumeric)', multiline=False)
        self.phone_number_input = TextInput(hint_text='Phone Number', multiline=False)

        self.hostel_spinner = Spinner(text='Select Hostel', values=('Hall 1', 'Hall 2', 'Hall 3', 'Hall 4'))
        self.rmno_spinner = Spinner(text='Select RMNO (Room Number)', values=[str(i) for i in range(1, 6)])
        self.gender_spinner = Spinner(text='Select Gender', values=('Male', 'Female'))
        self.booking_date_input = TextInput(hint_text='Booking Date', multiline=False)
        self.semester_spinner = Spinner(text='Select Semester', values=('Semester 1', 'Semester 2'))

        self.book_button = Button(text='Book', on_press=self.book)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='Booking Form'))
        layout.add_widget(self.reg_number_input)
        layout.add_widget(self.phone_number_input)
        layout.add_widget(self.hostel_spinner)
        layout.add_widget(self.rmno_spinner)
        layout.add_widget(self.gender_spinner)
        layout.add_widget(self.booking_date_input)
        layout.add_widget(self.semester_spinner)
        layout.add_widget(self.book_button)

        self.add_widget(layout)

        # Dictionary to store the mapping of halls to rooms
        self.hall_to_rooms = {
            'Hall 1': ['Room 1', 'Room 2', 'Room 3', 'Room 4', 'Room 5', 'Room 6', 'Room 7', 'Room 8', 'Room 9', 'Room 10', 'Room 11', 'Room 12'],
            'Hall 2': ['Room 1', 'Room 2', 'Room 3', 'Room 4', 'Room 5', 'Room 6', 'Room 7', 'Room 8', 'Room 9', 'Room 10', 'Room 11', 'Room 12'],
            'Hall 3': ['Room 1', 'Room 2', 'Room 3', 'Room 4', 'Room 5', 'Room 6', 'Room 7', 'Room 8', 'Room 9', 'Room 10', 'Room 11', 'Room 12'],
            'Hall 4': ['Room 1', 'Room 2', 'Room 3', 'Room 4', 'Room 5', 'Room 6', 'Room 7', 'Room 8', 'Room 9', 'Room 10', 'Room 11', 'Room 12'],
        }

        # Bind the update_rooms method to the on_text event of the hostel_spinner
        self.hostel_spinner.bind(on_text=self.update_rooms)

    def update_rooms(self, spinner, text):
        # You can update this method if necessary, but it's not required since the room selection is removed.
        pass

    def validate_reg_number(self, reg_number):
        # Validate reg_number to accept only numbers and letters
        return bool(re.match("^[a-zA-Z0-9]+$", reg_number))

    def is_room_booked(self, hostel, rmno):
        query = "SELECT * FROM Bookings WHERE hostel = %s AND rmno = %s"
        params = (hostel, rmno)
        result = self.db_manager.fetch_data(query, params)
        return bool(result)

    def book(self, instance):
        reg_number = self.reg_number_input.text
        phone_number = self.phone_number_input.text
        hostel = self.hostel_spinner.text
        rmno = self.rmno_spinner.text
        gender = self.gender_spinner.text
        booking_date = self.booking_date_input.text
        semester = self.semester_spinner.text

        # Validate reg_number
        if not self.validate_reg_number(reg_number):
            self.show_popup("Invalid Reg Number", "Reg Number should contain only numbers and letters.")
            return

        # Check if the room is already booked
        if self.is_room_booked(hostel, rmno):
            self.show_popup("Booking Failed", "This room is already booked. Please choose another room.")
            return

        query = "INSERT INTO Bookings (reg_number, phone_number, hostel, rmno, gender, booking_date, semester) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        params = (reg_number, phone_number, hostel, rmno, gender, booking_date, semester)

        if self.db_manager.execute_query(query, params):
            self.show_popup("Booking Successful", "Booking successful!")
        else:
            self.show_popup("Booking Failed", "Failed to book. Please try again.")

    def show_popup(self, title, content):
        popup = Popup(title=title, content=Label(text=content), size_hint=(None, None), size=(400, 200))
        popup.open()
        
class AccommodationApp(App):
    def build(self):
        db_manager = DatabaseManager()

        booking_form_screen = BookingFormScreen(db_manager, name='booking_form')
        login_screen = LoginScreen(db_manager, booking_form_screen, name='login')
        sign_up_screen = SignUpScreen(db_manager, login_screen, name='sign_up')

        screen_manager = ScreenManager()
        screen_manager.add_widget(login_screen)
        screen_manager.add_widget(sign_up_screen)
        screen_manager.add_widget(booking_form_screen)

        return screen_manager

    def on_stop(self):
        # Cleanup when the app is closed
        db_manager = DatabaseManager()
        del db_manager

if __name__ == '__main__':
    AccommodationApp().run()
