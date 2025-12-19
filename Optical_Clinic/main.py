import mysql.connector
import sys
import re
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from admin_window import AdminWindow
from optometrist_window import OptometristWindow
from sales_associate_window import SalesAssociateWindow

# Database connection setup.
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="opticalclinic_db"
)
db_cursor = db_connection.cursor(dictionary=True)

# Fetch employee from database based on ID and password.
def fetch_employee(employee_id, employee_password):
    sql_query = """
        SELECT * FROM Employees 
        WHERE employee_id=%s AND employee_pwd=%s
    """
    db_cursor.execute(sql_query, (employee_id, employee_password))
    return db_cursor.fetchone()

# Validate password requirements
def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character."
    return True, "Password is valid."

# Fetch employee by verification details (for password reset)
def fetch_employee_by_details(name, role, number):
    sql_query = """
        SELECT * FROM Employees 
        WHERE employee_name=%s AND employee_role=%s AND employee_cnum=%s
    """
    db_cursor.execute(sql_query, (name, role, number))
    return db_cursor.fetchone()

# Update employee password
def update_employee_password(employee_id, new_password):
    sql_query = """
        UPDATE Employees 
        SET employee_pwd=%s 
        WHERE employee_id=%s
    """
    db_cursor.execute(sql_query, (new_password, employee_id))
    db_connection.commit()

# CUSTOM DIALOG
class CustomDialog(QDialog):
    def __init__(self, title, message, icon_type=None, parent=None):
        super().__init__(parent)

        self.setFixedSize(350, 150)
        self.setWindowTitle(title)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 20)

        dialog_font = QFont("Futura Cyrillic Medium", 12)

        label = QLabel(message)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        label.setFont(dialog_font)

        ok_btn = QPushButton("Okay")
        ok_btn.setFixedSize(100, 35)
        ok_btn.setFont(dialog_font)
        ok_btn.clicked.connect(self.accept)

        ok_btn.setStyleSheet("""
            QPushButton {
                color: #fffff0;
                background-color: #f69623;
                border-radius: 15px;
            }
            QPushButton:hover {
                color: #f69623;
                background-color: #fffff0;
                border: 2px solid #f69623;
            }
        """)

        layout.addWidget(label)
        layout.addWidget(ok_btn, alignment=Qt.AlignCenter)

        self.setStyleSheet("""
            QDialog {
                background-color: #fffff0;
            }
        """)

# FORGOT PASSWORD VERIFICATION DIALOG
class ForgotPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedSize(400, 320)
        self.setWindowTitle("Forgot Password")
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 30)

        dialog_font = QFont("Futura Cyrillic Medium", 12)

        title_label = QLabel("Verify Your Identity")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Futura Cyrillic Medium", 14, QFont.Bold))

        # Name input with container
        name_container = QWidget()
        name_layout = QHBoxLayout(name_container)
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.setSpacing(0)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full Name")
        self.name_input.setMinimumHeight(35)
        self.name_input.setFont(dialog_font)
        self.name_input.setStyleSheet("background-color: #d9d9d9; border: none; padding: 5px; border-top-left-radius: 5px; border-bottom-left-radius: 5px;")

        name_layout.addWidget(self.name_input)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["Optometrist", "Sales Associate"])
        self.role_combo.setMinimumHeight(35)
        self.role_combo.setFont(dialog_font)
        self.role_combo.setStyleSheet("background-color: #d9d9d9; border: none; padding: 5px;")

        self.number_input = QLineEdit()
        self.number_input.setPlaceholderText("Contact Number")
        self.number_input.setMinimumHeight(35)
        self.number_input.setFont(dialog_font)
        self.number_input.setStyleSheet("background-color: #d9d9d9; border: none; padding: 5px;")

        btn_layout = QHBoxLayout()

        cancel_btn = QPushButton("Cancel")
        verify_btn = QPushButton("Verify")

        cancel_btn.setFixedSize(100, 35)
        verify_btn.setFixedSize(100, 35)

        cancel_btn.clicked.connect(self.reject)
        verify_btn.clicked.connect(self.accept)

        for btn in (cancel_btn, verify_btn):
            btn.setFont(dialog_font)
            btn.setStyleSheet("""
                QPushButton {
                    color: #fffff0;
                    background-color: #f69623;
                    border-radius: 15px;
                }
                QPushButton:hover {
                    color: #f69623;
                    background-color: #fffff0;
                    border: 2px solid #f69623;
                }
            """)

        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(verify_btn)
        btn_layout.addStretch()

        layout.addWidget(title_label)
        layout.addSpacing(20)
        layout.addWidget(QLabel("Name:"))
        layout.addWidget(name_container)
        layout.addWidget(QLabel("Role:"))
        layout.addWidget(self.role_combo)
        layout.addWidget(QLabel("Contact Number:"))
        layout.addWidget(self.number_input)
        layout.addSpacing(20)
        layout.addLayout(btn_layout)

        self.setStyleSheet("""
            QDialog {
                background-color: #fffff0;
            }
            QLabel {
                color: #333;
                font-family: 'Futura Cyrillic Medium';
            }
        """)

    def get_details(self):
        return {
            'name': self.name_input.text().strip(),
            'role': self.role_combo.currentText(),
            'number': self.number_input.text().strip()
        }

# RESET PASSWORD DIALOG
class ResetPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedSize(400, 280)
        self.setWindowTitle("Reset Password")
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 30)

        dialog_font = QFont("Futura Cyrillic Medium", 12)

        title_label = QLabel("Enter New Password")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Futura Cyrillic Medium", 14, QFont.Bold))

        info_label = QLabel("Password must be at least 8 characters with uppercase, lowercase, numbers, and special characters.")
        info_label.setWordWrap(True)
        info_label.setFont(QFont("Futura Cyrillic Medium", 9))
        info_label.setStyleSheet("color: #666;")

        # New password container with show/hide button
        new_pwd_container = QWidget()
        new_pwd_layout = QHBoxLayout(new_pwd_container)
        new_pwd_layout.setContentsMargins(0, 0, 0, 0)
        new_pwd_layout.setSpacing(0)

        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("New Password")
        self.new_password_input.setEchoMode(QLineEdit.Password)
        self.new_password_input.setMinimumHeight(35)
        self.new_password_input.setFont(dialog_font)
        self.new_password_input.setStyleSheet("background-color: #d9d9d9; border: none; padding: 5px; border-top-left-radius: 5px; border-bottom-left-radius: 5px;")

        self.show_new_pwd_btn = QPushButton("👁")
        self.show_new_pwd_btn.setFixedSize(40, 35)
        self.show_new_pwd_btn.setFont(QFont("Arial", 12))
        self.show_new_pwd_btn.setCursor(Qt.PointingHandCursor)
        self.show_new_pwd_btn.setCheckable(True)
        self.show_new_pwd_btn.setStyleSheet("""
            QPushButton {
                background-color: #d9d9d9;
                border: none;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c9c9c9;
            }
            QPushButton:checked {
                background-color: #f69623;
                color: white;
            }
        """)
        self.show_new_pwd_btn.clicked.connect(lambda: self.toggle_reset_password(self.new_password_input, self.show_new_pwd_btn))

        new_pwd_layout.addWidget(self.new_password_input)
        new_pwd_layout.addWidget(self.show_new_pwd_btn)

        # Confirm password container with show/hide button
        confirm_pwd_container = QWidget()
        confirm_pwd_layout = QHBoxLayout(confirm_pwd_container)
        confirm_pwd_layout.setContentsMargins(0, 0, 0, 0)
        confirm_pwd_layout.setSpacing(0)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Re-enter Password")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setMinimumHeight(35)
        self.confirm_password_input.setFont(dialog_font)
        self.confirm_password_input.setStyleSheet("background-color: #d9d9d9; border: none; padding: 5px; border-top-left-radius: 5px; border-bottom-left-radius: 5px;")

        self.show_confirm_pwd_btn = QPushButton("👁")
        self.show_confirm_pwd_btn.setFixedSize(40, 35)
        self.show_confirm_pwd_btn.setFont(QFont("Arial", 12))
        self.show_confirm_pwd_btn.setCursor(Qt.PointingHandCursor)
        self.show_confirm_pwd_btn.setCheckable(True)
        self.show_confirm_pwd_btn.setStyleSheet("""
            QPushButton {
                background-color: #d9d9d9;
                border: none;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c9c9c9;
            }
            QPushButton:checked {
                background-color: #f69623;
                color: white;
            }
        """)
        self.show_confirm_pwd_btn.clicked.connect(lambda: self.toggle_reset_password(self.confirm_password_input, self.show_confirm_pwd_btn))

        confirm_pwd_layout.addWidget(self.confirm_password_input)
        confirm_pwd_layout.addWidget(self.show_confirm_pwd_btn)

        btn_layout = QHBoxLayout()

        cancel_btn = QPushButton("Cancel")
        reset_btn = QPushButton("Reset")

        cancel_btn.setFixedSize(100, 35)
        reset_btn.setFixedSize(100, 35)

        cancel_btn.clicked.connect(self.reject)
        reset_btn.clicked.connect(self.validate_and_accept)

        for btn in (cancel_btn, reset_btn):
            btn.setFont(dialog_font)
            btn.setStyleSheet("""
                QPushButton {
                    color: #fffff0;
                    background-color: #f69623;
                    border-radius: 15px;
                }
                QPushButton:hover {
                    color: #f69623;
                    background-color: #fffff0;
                    border: 2px solid #f69623;
                }
            """)

        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(reset_btn)
        btn_layout.addStretch()

        layout.addWidget(title_label)
        layout.addSpacing(10)
        layout.addWidget(info_label)
        layout.addSpacing(15)
        layout.addWidget(new_pwd_container)
        layout.addWidget(confirm_pwd_container)
        layout.addSpacing(20)
        layout.addLayout(btn_layout)

        self.setStyleSheet("""
            QDialog {
                background-color: #fffff0;
            }
        """)

    def toggle_reset_password(self, input_field, button):
        if button.isChecked():
            input_field.setEchoMode(QLineEdit.Normal)
        else:
            input_field.setEchoMode(QLineEdit.Password)

    def validate_and_accept(self):
        new_pwd = self.new_password_input.text()
        confirm_pwd = self.confirm_password_input.text()

        if new_pwd != confirm_pwd:
            CustomDialog(
                title="Error",
                message="Passwords do not match.",
                parent=self
            ).exec_()
            return

        is_valid, message = validate_password(new_pwd)
        if not is_valid:
            CustomDialog(
                title="Invalid Password",
                message=message,
                parent=self
            ).exec_()
            return

        self.accept()

    def get_password(self):
        return self.new_password_input.text()

# ADMIN PASSWORD DIALOG
class CustomAdminPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedSize(350, 200)
        self.setWindowTitle("Admin Login")
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 30)

        dialog_font = QFont("Futura Cyrillic Medium", 12)

        title_label = QLabel("Enter Admin Password")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(dialog_font)

        # Admin password container with show/hide button
        admin_pwd_container = QWidget()
        admin_pwd_layout = QHBoxLayout(admin_pwd_container)
        admin_pwd_layout.setContentsMargins(0, 0, 0, 0)
        admin_pwd_layout.setSpacing(0)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(35)
        self.password_input.setFont(dialog_font)
        self.password_input.setStyleSheet("background-color: #d9d9d9; border: none; border-top-left-radius: 5px; border-bottom-left-radius: 5px;")

        self.show_admin_pwd_btn = QPushButton("👁")
        self.show_admin_pwd_btn.setFixedSize(40, 35)
        self.show_admin_pwd_btn.setFont(QFont("Arial", 12))
        self.show_admin_pwd_btn.setCursor(Qt.PointingHandCursor)
        self.show_admin_pwd_btn.setCheckable(True)
        self.show_admin_pwd_btn.setStyleSheet("""
            QPushButton {
                background-color: #d9d9d9;
                border: none;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c9c9c9;
            }
            QPushButton:checked {
                background-color: #f69623;
                color: white;
            }
        """)
        self.show_admin_pwd_btn.clicked.connect(self.toggle_admin_password)

        admin_pwd_layout.addWidget(self.password_input)
        admin_pwd_layout.addWidget(self.show_admin_pwd_btn)

        btn_layout = QHBoxLayout()

        cancel_btn = QPushButton("Cancel")
        login_btn = QPushButton("Login")

        cancel_btn.setFixedSize(100, 35)
        login_btn.setFixedSize(100, 35)

        cancel_btn.clicked.connect(self.reject)
        login_btn.clicked.connect(self.accept)

        for btn in (cancel_btn, login_btn):
            btn.setFont(dialog_font)
            btn.setStyleSheet("""
                QPushButton {
                    color: #fffff0;
                    background-color: #f69623;
                    border-radius: 15px;
                }
                QPushButton:hover {
                    color: #f69623;
                    background-color: #fffff0;
                    border: 2px solid #f69623;
                }
            """)

        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(login_btn)
        btn_layout.addStretch()

        layout.addWidget(title_label)
        layout.addSpacing(10)
        layout.addWidget(admin_pwd_container)
        layout.addSpacing(20)
        layout.addLayout(btn_layout)

        self.setStyleSheet("""
            QDialog {
                background-color: #fffff0;
            }
        """)

    def toggle_admin_password(self):
        if self.show_admin_pwd_btn.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)

    def get_password(self):
        return self.password_input.text().strip()

# Main application window class.
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CJCEyeSite Management System")

        # Window size and icon settings.
        self.resize(1200, 800)
        self.setMinimumSize(1000, 750)
        self.setWindowIcon(QIcon(
            r"C:/Users/Ianne/Programming/Projects/Python/Optical_Clinic/Icons/eyesite_orange_logo.png"
        ))

        # Child window references.
        self.admin_window = None
        self.optometrist_window = None
        self.sales_window = None

        # Central widget setup.
        self.central_widget = QWidget()
        self.central_widget.setStyleSheet("background-color: #fffff0;")
        self.setCentralWidget(self.central_widget)

        # Left panel widget and layout.
        self.left_panel_widget = QWidget()
        self.left_panel_widget.setObjectName("leftPanel")
        self.left_panel_layout = QVBoxLayout(self.left_panel_widget)
        self.left_panel_layout.setContentsMargins(0, 0, 0, 0)
        self.left_panel_layout.setSpacing(0)

        # Right panel widget and layout.
        self.right_panel_widget = QWidget()
        self.right_panel_widget.setStyleSheet("background-color: #fffff0;")
        self.right_panel_layout = QVBoxLayout(self.right_panel_widget)
        self.right_panel_layout.setAlignment(Qt.AlignCenter)
        self.right_panel_layout.setContentsMargins(40, 40, 40, 40)

        # Content box for login form.
        self.content_box_widget = QWidget()
        self.content_box_widget.setMaximumWidth(450)
        self.content_box_layout = QVBoxLayout(self.content_box_widget)
        self.content_box_layout.setAlignment(Qt.AlignCenter)
        self.content_box_layout.setContentsMargins(30, 30, 40, 30)

        # Header label for welcome message.
        self.header_label = QLabel("Welcome")
        self.header_label.setFont(QFont("Futura Cyrillic Medium", 35, QFont.Medium))
        self.header_label.setAlignment(Qt.AlignCenter)
        self.header_label.setStyleSheet("color: #f69623")

        # Font for input field labels.
        self.field_label_font = QFont("Futura Cyrillic Medium", 15, QFont.Medium)

        # Employee ID input and label.
        self.id_label = QLabel("Employee ID")
        self.id_label.setFont(self.field_label_font)
        self.id_input = QLineEdit()
        self.id_input.setFont(self.field_label_font)
        self.id_input.setMinimumHeight(50)
        self.id_input.setStyleSheet("background-color: #d9d9d9; border: none;")

        # Password input and label.
        self.password_label = QLabel("Password")
        self.password_label.setFont(self.field_label_font)
        
        # Password container with show/hide button
        password_container = QWidget()
        password_layout = QHBoxLayout(password_container)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(0)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(self.field_label_font)
        self.password_input.setMinimumHeight(50)
        self.password_input.setStyleSheet("background-color: #d9d9d9; border: none; border-top-left-radius: 5px; border-bottom-left-radius: 5px;")
        
        self.show_password_btn = QPushButton("👁")
        self.show_password_btn.setFixedSize(50, 50)
        self.show_password_btn.setFont(QFont("Arial", 16))
        self.show_password_btn.setCursor(Qt.PointingHandCursor)
        self.show_password_btn.setCheckable(True)
        self.show_password_btn.setStyleSheet("""
            QPushButton {
                background-color: #d9d9d9;
                border: none;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c9c9c9;
            }
            QPushButton:checked {
                background-color: #f69623;
                color: white;
            }
        """)
        self.show_password_btn.clicked.connect(self.toggle_password_visibility)
        
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.show_password_btn)

        # Forgot Password button
        self.forgot_password_btn = QPushButton("Forgot Password?")
        self.forgot_password_btn.setFont(QFont("Futura Cyrillic Medium", 11))
        self.forgot_password_btn.setStyleSheet("""
            QPushButton {
                color: #888;
                border: none;
                text-align: left;
            }
            QPushButton:hover {
                color: #f69623;
            }
        """)
        self.forgot_password_btn.setCursor(Qt.PointingHandCursor)
        self.forgot_password_btn.clicked.connect(self.handle_forgot_password)

        # Login buttons font.
        self.button_font = QFont("Futura Cyrillic Medium", 15, QFont.Medium)

        # Employee login button.
        self.login_btn = QPushButton("Login")
        self.login_btn.setFont(self.button_font)
        self.login_btn.setMinimumHeight(50)
        self.login_btn.setStyleSheet("""
            QPushButton {
                color: #fffff0;
                background-color: #f69623;
                border-radius: 15px;
            }
            QPushButton:hover {
                color: #f69623;
                background-color: #fffff0;
                border: 2px solid #f69623;
            }
        """)

        # Admin login button.
        self.admin_login_btn = QPushButton("Login as Administrator")
        self.admin_login_btn.setFont(self.button_font)
        self.admin_login_btn.setMinimumHeight(40)
        self.admin_login_btn.setStyleSheet("""
            QPushButton {
                color: #f69623;
                border: none;
            }
            QPushButton:hover {
                color: #d9d9d9;
            }
        """)

        # Add widgets to content box layout.
        self.content_box_layout.addWidget(self.header_label)
        self.content_box_layout.addSpacing(35)
        self.content_box_layout.addWidget(self.id_label)
        self.content_box_layout.addWidget(self.id_input)
        self.content_box_layout.addWidget(self.password_label)
        self.content_box_layout.addWidget(password_container)
        self.content_box_layout.addWidget(self.forgot_password_btn, alignment=Qt.AlignRight)
        self.content_box_layout.addSpacing(35)
        self.content_box_layout.addWidget(self.login_btn)
        self.content_box_layout.addWidget(self.admin_login_btn)
        self.right_panel_layout.addWidget(self.content_box_widget)

        # Main splitter for left and right panels.
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.left_panel_widget)
        self.splitter.addWidget(self.right_panel_widget)
        self.splitter.setHandleWidth(0)

        # Central layout for main window.
        self.central_layout = QHBoxLayout(self.central_widget)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.addWidget(self.splitter)

        # Connect buttons to login functions.
        self.login_btn.clicked.connect(self.handle_employee_login)
        self.admin_login_btn.clicked.connect(self.handle_admin_login)

        # Set initial left panel background.
        self.update_left_panel_background()

    # Toggle password visibility
    def toggle_password_visibility(self):
        if self.show_password_btn.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)

    # Handle forgot password flow
    def handle_forgot_password(self):
        # Step 1: Verify identity
        verify_dialog = ForgotPasswordDialog(self)
        if verify_dialog.exec_() != QDialog.Accepted:
            return

        details = verify_dialog.get_details()
        employee = fetch_employee_by_details(details['name'], details['role'], details['number'])

        if not employee:
            CustomDialog(
                title="Verification Failed",
                message="No matching employee found. Please check your details.",
                parent=self
            ).exec_()
            return

        # Step 2: Reset password
        reset_dialog = ResetPasswordDialog(self)
        if reset_dialog.exec_() != QDialog.Accepted:
            return

        new_password = reset_dialog.get_password()
        update_employee_password(employee['employee_id'], new_password)

        CustomDialog(
            title="Success",
            message="Password has been reset successfully. Please login with your new password.",
            parent=self
        ).exec_()

        # Clear input fields
        self.id_input.clear()
        self.password_input.clear()

    # Update left panel background based on window state.
    def update_left_panel_background(self):
        is_full_or_max = (
            self.isFullScreen() or
            self.windowState() & Qt.WindowMaximized
        )

        if is_full_or_max:
            image_path = r"C:/Users/Ianne/Programming/Projects/Python/Optical_Clinic/Icons/left_login_bg_2.png"
        else:
            image_path = r"C:/Users/Ianne/Programming/Projects/Python/Optical_Clinic/Icons/left_login_bg_1.png"

        self.left_panel_widget.setStyleSheet(f"""
            QWidget#leftPanel {{
                background-image: url("{image_path}");
                background-repeat: no-repeat;
                background-position: center;
            }}
        """)

    # Handle window state changes.
    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            self.update_left_panel_background()
        super().changeEvent(event)

    # Handle full screen mode.
    def showFullScreen(self):
        super().showFullScreen()
        self.update_left_panel_background()

    # Handle normal window mode.
    def showNormal(self):
        super().showNormal()
        self.update_left_panel_background()

    # Adjust splitter size on resize.
    def resizeEvent(self, event):
        super().resizeEvent(event)
        total_width = self.width()
        self.splitter.setSizes([total_width // 2, total_width // 2])

    # Admin login handling function.
    def handle_admin_login(self):
        dialog = CustomAdminPasswordDialog(self)

        if dialog.exec_() == QDialog.Accepted:
            if dialog.get_password() == "opticalclinic_admin":
                CustomDialog(
                    title="Admin Login",
                    message="Welcome Admin!",
                    icon_type="success",
                    parent=self
                ).exec_()

                # Show admin window and close main window.
                self.admin_window = AdminWindow()
                self.admin_window.show()
                self.close()
            else:
                CustomDialog(
                    title="Login Failed",
                    message="Incorrect admin password.",
                    icon_type="error",
                    parent=self
                ).exec_()

    # Employee login handling function.
    def handle_employee_login(self):
        employee = fetch_employee(
            self.id_input.text().strip(),
            self.password_input.text().strip()
        )

        if not employee:
            CustomDialog(
                title="Login Failed",
                message="Incorrect ID or Password.",
                icon_type="error",
                parent=self
            ).exec_()
            return

        CustomDialog(
            title="Login Success",
            message=f"Welcome {employee['employee_name']}!",
            icon_type="success",
            parent=self
        ).exec_()

        # Show employee window based on role.
        if employee["employee_role"] == "Optometrist":
            self.optometrist_window = OptometristWindow()
            self.optometrist_window.show()
        elif employee["employee_role"] == "Sales Associate":
            self.sales_window = SalesAssociateWindow()
            self.sales_window.show()

        self.close()

# Run the application.
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())