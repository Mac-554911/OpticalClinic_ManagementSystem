import sys
import re
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import mysql.connector

# DATABASE MANAGER
class Database:
    def __init__(self):
        self.connect_db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="opticalclinic_db"
        )
        self.cursor = self.connect_db.cursor(dictionary=True)

    # SELECT queries
    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.cursor.fetchall()

    # INSERT, UPDATE, DELETE queries
    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        self.connect_db.commit()

db = Database()

# ADMIN WINDOW
class AdminWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CJCEyeSite Management System | Admin")
        self.setWindowIcon(QIcon(
            r"C:/Users/Ianne/Programming/Projects/Python/Optical_Clinic/Icons/eyesite_orange_logo.png"
        ))

        self.setWindowFlags(
            Qt.Window |
            Qt.WindowMinimizeButtonHint |
            Qt.WindowCloseButtonHint
        )
        self.panel_history = []
        self.current_panel = None
        self.current_table_widget = None
        self.all_data = []  # Store all data for search functionality

        self.init_ui()
        self.showMaximized()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        self.init_left_panel()
        self.init_right_panel()

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.left_panel_widget)
        self.splitter.addWidget(self._right_panel_widget)

        # 1:3 ratio
        self.splitter.setSizes([250, 750])
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #f69623;
                width: 2px;
            }
        """)

        layout.addWidget(self.splitter)

    # LEFT PANEL
    def init_left_panel(self):
        self.left_panel_widget = QWidget()
        self.left_panel_widget.setFixedWidth(350)
        self.left_panel_widget.setStyleSheet("background-color: #373737")

        layout = QVBoxLayout(self.left_panel_widget)
        layout.setContentsMargins(30, 40, 30, 60)

        # LOGO
        company_logo = QLabel()
        company_logo.setPixmap(QIcon(
            r"C:/Users/Ianne/Programming/Projects/Python/Optical_Clinic/Icons/eyesite_orange_logo.png"
        ).pixmap(125, 125))
        layout.addWidget(company_logo, alignment=Qt.AlignLeft)
        layout.addSpacing(35)

        # BUTTONS
        button_font = QFont("Futura Cyrillic Medium", 15, QFont.Bold)

        self.employees_button = QPushButton("EMPLOYEES")
        self.employees_button.setFont(button_font)
        self.employees_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 2px solid #f69623;
                color: #f69623;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #f69623;
                color: #373737;
            }
        """)
        self.employees_button.clicked.connect(self.show_employees_panel)
        layout.addWidget(self.employees_button)
        
        layout.addSpacing(15)

        self.products_button = QPushButton("PRODUCTS")
        self.products_button.setFont(button_font)
        self.products_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 2px solid #f69623;
                color: #f69623;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #f69623;
                color: #373737;
            }
        """)
        self.products_button.clicked.connect(self.show_products_panel)
        layout.addWidget(self.products_button)

        layout.addStretch()

        # LOGOUT BUTTON
        logout_button = QPushButton("LOGOUT")
        logout_button.setFont(QFont("Futura Cyrillic Medium", 12))
        logout_button.setStyleSheet("""
            QPushButton {
                text-align: left;
                color: #f69623;
                background: none;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                color: #fffff0;
            }
        """)
        logout_button.clicked.connect(self.handle_logout)
        layout.addSpacing(20)
        layout.addWidget(logout_button, alignment=Qt.AlignLeft)

    # RIGHT PANEL
    def init_right_panel(self):
        self._right_panel_widget = QWidget()
        self._right_panel_widget.setStyleSheet("background-color:#fffff0;")

        self._right_layout = QVBoxLayout(self._right_panel_widget)
        self._right_layout.setContentsMargins(12, 12, 12, 18)

        self._back_button = QPushButton("BACK")
        self._back_button.setFixedSize(120, 45)
        self._back_button.setFont(QFont("Futura Cyrillic Medium", 12))
        self._back_button.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: #f69623;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #ff8c00;
            }
        """)
        self._back_button.clicked.connect(self.go_back)
        self._right_layout.addWidget(self._back_button, alignment=Qt.AlignLeft)

        # HOME LOGO - Create container to maintain centering
        self.home_container = QWidget()
        home_layout = QVBoxLayout(self.home_container)
        home_layout.setContentsMargins(0, 0, 0, 0)
        
        home_label = QLabel()
        home_label.setPixmap(QIcon(
            r"C:/Users/Ianne/Programming/Projects/Python/Optical_Clinic/Icons/eyesite_text_logo.png"
        ).pixmap(650, 250))
        home_layout.addWidget(home_label, alignment=Qt.AlignCenter)
        
        self._right_layout.addWidget(self.home_container, alignment=Qt.AlignCenter)
        self.current_panel = self.home_container

    # PANEL MANAGEMENT
    def save_current_panel(self):
        if self.current_panel:
            self.panel_history.append(self.current_panel)

    def clear_right_panel(self):
        for i in reversed(range(self._right_layout.count())):
            widget = self._right_layout.itemAt(i).widget()
            if widget and widget != self._back_button:
                widget.setParent(None)

    def go_back(self):
        if self.panel_history:
            self.clear_right_panel()
            panel = self.panel_history.pop()
            self._right_layout.addWidget(self._back_button, alignment=Qt.AlignLeft)
            
            # Check if it's the home container to maintain proper centering
            if panel == self.home_container:
                self._right_layout.addWidget(panel, alignment=Qt.AlignCenter)
            else:
                self._right_layout.addWidget(panel)
            
            self.current_panel = panel

    def pretty_field_name(self, field):
        mapping = {
            # EMPLOYEES
            "employee_id": "Employee ID",
            "employee_name": "Full Name",
            "employee_role": "Role",
            "employee_cnum": "Contact Number",
            "employee_email": "Email Address",
            "employee_pwd": "Password",

            # PRODUCTS
            "product_id": "Product ID",
            "product_name": "Product Name",
            "product_model": "Model",
            "product_color": "Color",
            "product_price": "Price",
            "product_stock": "Stock Quantity",
            "stock_status": "Stock Status",
        }
        return mapping.get(field, field.replace("_", " ").title())

    # VALIDATION METHODS
    def validate_employee_name(self, name, current_id=None):
        """Check if employee name already exists (excluding current record)"""
        if not name:
            return False, ""
        
        all_employees = db.query("SELECT employee_id, employee_name FROM Employees")
        for emp in all_employees:
            if emp['employee_name'].lower() == name.lower():
                if current_id is None or str(emp['employee_id']) != str(current_id):
                    return False, "Employee name already exists"
        return True, ""

    def validate_employee_email(self, email, current_id=None):
        """Check if email is valid and unique"""
        if not email:
            return False, ""
        
        # Email format validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "Invalid email format"
        
        # Check uniqueness
        all_employees = db.query("SELECT employee_id, employee_email FROM Employees")
        for emp in all_employees:
            if emp['employee_email'].lower() == email.lower():
                if current_id is None or str(emp['employee_id']) != str(current_id):
                    return False, "Email already exists"
        return True, ""

    def validate_employee_contact(self, contact, current_id=None):
        """Check if contact number is valid and unique"""
        if not contact:
            return False, ""
        
        # Contact format validation (Philippine format)
        contact_pattern = r'^(09|\+639)\d{9}$'
        if not re.match(contact_pattern, contact):
            return False, "Invalid contact number format (e.g., 09123456789)"
        
        # Check uniqueness
        all_employees = db.query("SELECT employee_id, employee_cnum FROM Employees")
        for emp in all_employees:
            if emp['employee_cnum'] == contact:
                if current_id is None or str(emp['employee_id']) != str(current_id):
                    return False, "Contact number already exists"
        return True, ""

    def validate_password(self, password):
        """Validate password strength"""
        if not password:
            return False, ""
        
        if len(password) < 8 or len(password) > 15:
            return False, "Password must be 8-15 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>-_]', password):
            return False, "Password must contain at least one symbol"
        
        return True, ""

    def validate_product_name(self, name, current_id=None):
        """Check if product name already exists (excluding current record)"""
        if not name:
            return False, ""
        
        all_products = db.query("SELECT product_id, product_name FROM Products")
        for prod in all_products:
            if prod['product_name'].lower() == name.lower():
                if current_id is None or str(prod['product_id']) != str(current_id):
                    return False, "Product name already exists"
        return True, ""

    def set_field_error(self, field_widget, error_label, error_msg):
        """Set field to error state"""
        field_widget.setStyleSheet("""
            QLineEdit {
                border: 2px solid red;
                border-radius: 3px;
                padding: 5px;
                background-color: #ffe6e6;
            }
        """)
        error_label.setText(error_msg)
        error_label.setStyleSheet("color: red; font-size: 9pt;")

    def clear_field_error(self, field_widget, error_label):
        """Clear field error state"""
        if field_widget.isReadOnly():
            field_widget.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #d9d9d9;
                    border-radius: 3px;
                    padding: 5px;
                    background-color: #e0e0e0;
                }
            """)
        else:
            field_widget.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #d9d9d9;
                    border-radius: 3px;
                    padding: 5px;
                    background-color: white;
                }
            """)
        error_label.setText("")

    # EMPLOYEES PANEL
    def show_employees_panel(self):
        self.save_current_panel()
        self.clear_right_panel()

        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header with title and search bar
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Employees")
        title_label.setFont(QFont("Futura Cyrillic Medium", 20, QFont.Bold))
        title_label.setStyleSheet("color: #373737;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.setFixedSize(250, 35)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #f69623;
                border-radius: 5px;
                padding: 5px 10px;
                background-color: white;
            }
        """)
        self.search_input.textChanged.connect(self.filter_employees_table)
        header_layout.addWidget(self.search_input)

        main_layout.addLayout(header_layout)
        main_layout.addSpacing(15)

        # Table
        self.all_data = db.query("SELECT * FROM Employees")
        self.current_headers = ["employee_id", "employee_name", "employee_role", "employee_cnum", "employee_email", "employee_pwd"]
        
        self.current_table_widget = self.create_table(self.all_data, self.current_headers)
        self.current_table_widget.itemSelectionChanged.connect(self.on_employee_row_selected)
        
        main_layout.addWidget(self.current_table_widget)

        # Bottom section: Form (left) and Buttons (right)
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)

        # LEFT: Form fields
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 10, 0, 0)

        form_grid = QGridLayout()
        form_grid.setHorizontalSpacing(15)
        form_grid.setVerticalSpacing(10)

        fields = ["employee_id", "employee_name", "employee_role", "employee_cnum", "employee_email", "employee_pwd"]
        self.employee_inputs = {}
        self.employee_error_labels = {}

        for index, field in enumerate(fields):
            label = QLabel(self.pretty_field_name(field))
            label.setFont(QFont("Futura Cyrillic Medium", 10))
            line_edit = QLineEdit()
            line_edit.setFixedHeight(30)
            line_edit.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #d9d9d9;
                    border-radius: 3px;
                    padding: 5px;
                    background-color: white;
                }
            """)
            
            # Error label
            error_label = QLabel("")
            error_label.setWordWrap(True)
            
            if field == "employee_id":
                line_edit.setReadOnly(True)
                line_edit.setStyleSheet("""
                    QLineEdit {
                        border: 1px solid #d9d9d9;
                        border-radius: 3px;
                        padding: 5px;
                        background-color: #e0e0e0;
                    }
                """)
            
            form_grid.addWidget(label, index * 2, 0, alignment=Qt.AlignRight)
            form_grid.addWidget(line_edit, index * 2, 1)
            form_grid.addWidget(error_label, index * 2 + 1, 1)
            
            self.employee_inputs[field] = line_edit
            self.employee_error_labels[field] = error_label

        form_layout.addLayout(form_grid)
        form_layout.addStretch()

        bottom_layout.addWidget(form_container, 3)

        # RIGHT: Action buttons
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setContentsMargins(0, 10, 0, 0)
        button_layout.setSpacing(10)

        add_btn = QPushButton("Add")
        update_btn = QPushButton("Update")
        delete_btn = QPushButton("Delete")

        for btn in [add_btn, update_btn, delete_btn]:
            btn.setFixedSize(120, 40)
            btn.setFont(QFont("Futura Cyrillic Medium", 11))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f69623;
                    color: white;
                    border: none;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #ff8c00;
                }
            """)

        add_btn.clicked.connect(self.add_employee_db)
        update_btn.clicked.connect(self.update_employee_db)
        delete_btn.clicked.connect(self.delete_employee_db)

        button_layout.addWidget(add_btn)
        button_layout.addWidget(update_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addStretch()

        bottom_layout.addWidget(button_container, 1)

        main_layout.addLayout(bottom_layout)

        self._right_layout.addWidget(self._back_button, alignment=Qt.AlignLeft)
        self._right_layout.addWidget(main_container)
        self.current_panel = main_container

    def create_table(self, data, headers):
        table = QTableWidget(len(data), len(headers))
        pretty_headers = [self.pretty_field_name(h) for h in headers]
        table.setHorizontalHeaderLabels(pretty_headers)
        
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.setAlternatingRowColors(True)
        
        table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                background-color: #f9f9f9;
                alternate-background-color: #f0f0f0;
                gridline-color: #ddd;
            }
            QHeaderView::section {
                background-color: #f69623;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #ffd9b3;
                color: #373737;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)

        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.horizontalHeader().setHighlightSections(False)

        for row, item_data in enumerate(data):
            for col, header in enumerate(headers):
                table.setItem(row, col, QTableWidgetItem(str(item_data.get(header, ""))))

        return table

    def on_employee_row_selected(self):
        if self.current_table_widget.currentRow() >= 0:
            selected_row = self.current_table_widget.currentRow()
            
            for col, field in enumerate(self.current_headers):
                cell_value = self.current_table_widget.item(selected_row, col)
                if cell_value and field in self.employee_inputs:
                    self.employee_inputs[field].setText(cell_value.text())
                    # Clear any error states
                    if field in self.employee_error_labels:
                        self.clear_field_error(self.employee_inputs[field], self.employee_error_labels[field])

    def filter_employees_table(self):
        search_text = self.search_input.text().lower()
        
        if not search_text:
            filtered_data = self.all_data
        else:
            filtered_data = [
                row for row in self.all_data
                if any(search_text in str(value).lower() for value in row.values())
            ]
        
        # Refresh table with filtered data
        parent_layout = self.current_table_widget.parent().layout()
        index = parent_layout.indexOf(self.current_table_widget)
        
        self.current_table_widget.setParent(None)
        self.current_table_widget = self.create_table(filtered_data, self.current_headers)
        self.current_table_widget.itemSelectionChanged.connect(self.on_employee_row_selected)
        parent_layout.insertWidget(index, self.current_table_widget)

    def refresh_employees_table(self):
        self.all_data = db.query("SELECT * FROM Employees")
        self.search_input.clear()
        
        parent_layout = self.current_table_widget.parent().layout()
        index = parent_layout.indexOf(self.current_table_widget)
        
        self.current_table_widget.setParent(None)
        self.current_table_widget = self.create_table(self.all_data, self.current_headers)
        self.current_table_widget.itemSelectionChanged.connect(self.on_employee_row_selected)
        parent_layout.insertWidget(index, self.current_table_widget)

    def clear_employee_form(self):
        for field in self.employee_inputs:
            self.employee_inputs[field].clear()
            if field in self.employee_error_labels:
                self.clear_field_error(self.employee_inputs[field], self.employee_error_labels[field])

    def add_employee_db(self):
        # Clear all previous errors
        for field in self.employee_error_labels:
            self.clear_field_error(self.employee_inputs[field], self.employee_error_labels[field])
        
        fields = ["employee_name", "employee_role", "employee_cnum", "employee_email", "employee_pwd"]
        values = [self.employee_inputs[f].text() for f in fields]
        
        # Check if all fields are filled
        if not all(values):
            QMessageBox.warning(self, "Warning", "Please fill all fields.")
            return
        
        # Validate each field
        has_error = False
        
        # Validate name uniqueness
        valid, error_msg = self.validate_employee_name(values[0])
        if not valid:
            self.set_field_error(self.employee_inputs["employee_name"], 
                               self.employee_error_labels["employee_name"], error_msg)
            has_error = True
        
        # Validate contact
        valid, error_msg = self.validate_employee_contact(values[2])
        if not valid:
            self.set_field_error(self.employee_inputs["employee_cnum"], 
                               self.employee_error_labels["employee_cnum"], error_msg)
            has_error = True
        
        # Validate email
        valid, error_msg = self.validate_employee_email(values[3])
        if not valid:
            self.set_field_error(self.employee_inputs["employee_email"], 
                               self.employee_error_labels["employee_email"], error_msg)
            has_error = True
        
        # Validate password
        valid, error_msg = self.validate_password(values[4])
        if not valid:
            self.set_field_error(self.employee_inputs["employee_pwd"], 
                               self.employee_error_labels["employee_pwd"], error_msg)
            has_error = True
        
        if has_error:
            QMessageBox.warning(self, "Validation Error", "Please fix the errors highlighted in red.")
            return
        
        db.execute("INSERT INTO Employees (employee_name, employee_role, employee_cnum, employee_email, employee_pwd) VALUES (%s,%s,%s,%s,%s)", values)
        QMessageBox.information(self, "Success", "Employee added successfully.")
        self.refresh_employees_table()
        self.clear_employee_form()

    def update_employee_db(self):
        employee_id = self.employee_inputs["employee_id"].text()
        
        if not employee_id:
            QMessageBox.warning(self, "Warning", "Please select an employee to update.")
            return
        
        # Clear all previous errors
        for field in self.employee_error_labels:
            self.clear_field_error(self.employee_inputs[field], self.employee_error_labels[field])
        
        fields = ["employee_name", "employee_role", "employee_cnum", "employee_email", "employee_pwd"]
        values = [self.employee_inputs[f].text() for f in fields]
        
        if not all(values):
            QMessageBox.warning(self, "Warning", "Please fill all fields.")
            return
        
        # Validate each field
        has_error = False
        
        # Validate name uniqueness (excluding current record)
        valid, error_msg = self.validate_employee_name(values[0], employee_id)
        if not valid:
            self.set_field_error(self.employee_inputs["employee_name"], 
                               self.employee_error_labels["employee_name"], error_msg)
            has_error = True
        
        # Validate contact (excluding current record)
        valid, error_msg = self.validate_employee_contact(values[2], employee_id)
        if not valid:
            self.set_field_error(self.employee_inputs["employee_cnum"], 
                               self.employee_error_labels["employee_cnum"], error_msg)
            has_error = True
        
        # Validate email (excluding current record)
        valid, error_msg = self.validate_employee_email(values[3], employee_id)
        if not valid:
            self.set_field_error(self.employee_inputs["employee_email"], 
                               self.employee_error_labels["employee_email"], error_msg)
            has_error = True
        
        # Validate password
        valid, error_msg = self.validate_password(values[4])
        if not valid:
            self.set_field_error(self.employee_inputs["employee_pwd"], 
                               self.employee_error_labels["employee_pwd"], error_msg)
            has_error = True
        
        if has_error:
            QMessageBox.warning(self, "Validation Error", "Please fix the errors highlighted in red.")
            return
        
        db.execute("UPDATE Employees SET employee_name=%s, employee_role=%s, employee_cnum=%s, employee_email=%s, employee_pwd=%s WHERE employee_id=%s",
                   (*values, employee_id))
        QMessageBox.information(self, "Success", "Employee updated successfully.")
        self.refresh_employees_table()
        self.clear_employee_form()

    def delete_employee_db(self):
        employee_id = self.employee_inputs["employee_id"].text()
        
        if not employee_id:
            QMessageBox.warning(self, "Warning", "Please select an employee to delete.")
            return
        
        reply = QMessageBox.question(self, "Confirm Delete", 
                                      f"Are you sure you want to delete employee ID {employee_id}?",
                                      QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            db.execute("DELETE FROM Employees WHERE employee_id=%s", (employee_id,))
            QMessageBox.information(self, "Success", "Employee deleted successfully.")
            self.refresh_employees_table()
            self.clear_employee_form()

    # PRODUCTS PANEL
    def show_products_panel(self):
        self.save_current_panel()
        self.clear_right_panel()

        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header with title and search bar
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Products")
        title_label.setFont(QFont("Futura Cyrillic Medium", 20, QFont.Bold))
        title_label.setStyleSheet("color: #373737;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Search bar
        self.product_search_input = QLineEdit()
        self.product_search_input.setPlaceholderText("Search...")
        self.product_search_input.setFixedSize(250, 35)
        self.product_search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #f69623;
                border-radius: 5px;
                padding: 5px 10px;
                background-color: white;
            }
        """)
        self.product_search_input.textChanged.connect(self.filter_products_table)
        header_layout.addWidget(self.product_search_input)

        main_layout.addLayout(header_layout)
        main_layout.addSpacing(15)

        # Table
        self.all_product_data = db.query("SELECT * FROM Products")
        self.current_product_headers = ["product_id", "product_name", "product_model", "product_color", "product_price", "product_stock", "stock_status"]
        
        self.current_product_table = self.create_table(self.all_product_data, self.current_product_headers)
        self.current_product_table.itemSelectionChanged.connect(self.on_product_row_selected)
        
        main_layout.addWidget(self.current_product_table)

        # Bottom section: Form (left) and Buttons (right)
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)

        # LEFT: Form fields
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 10, 0, 0)

        form_grid = QGridLayout()
        form_grid.setHorizontalSpacing(15)
        form_grid.setVerticalSpacing(10)

        fields = ["product_id", "product_name", "product_model", "product_color", "product_price", "product_stock", "stock_status"]
        self.product_inputs = {}
        self.product_error_labels = {}

        for index, field in enumerate(fields):
            label = QLabel(self.pretty_field_name(field))
            label.setFont(QFont("Futura Cyrillic Medium", 10))
            line_edit = QLineEdit()
            line_edit.setFixedHeight(30)
            line_edit.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #d9d9d9;
                    border-radius: 3px;
                    padding: 5px;
                    background-color: white;
                }
            """)
            
            # Error label
            error_label = QLabel("")
            error_label.setWordWrap(True)
            
            if field == "product_id":
                line_edit.setReadOnly(True)
                line_edit.setStyleSheet("""
                    QLineEdit {
                        border: 1px solid #d9d9d9;
                        border-radius: 3px;
                        padding: 5px;
                        background-color: #e0e0e0;
                    }
                """)
            
            form_grid.addWidget(label, index * 2, 0, alignment=Qt.AlignRight)
            form_grid.addWidget(line_edit, index * 2, 1)
            form_grid.addWidget(error_label, index * 2 + 1, 1)
            
            self.product_inputs[field] = line_edit
            self.product_error_labels[field] = error_label

        form_layout.addLayout(form_grid)
        form_layout.addStretch()

        bottom_layout.addWidget(form_container, 3)

        # RIGHT: Action buttons
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setContentsMargins(0, 10, 0, 0)
        button_layout.setSpacing(10)

        add_btn = QPushButton("Add")
        update_btn = QPushButton("Update")
        delete_btn = QPushButton("Delete")

        for btn in [add_btn, update_btn, delete_btn]:
            btn.setFixedSize(120, 40)
            btn.setFont(QFont("Futura Cyrillic Medium", 11))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f69623;
                    color: white;
                    border: none;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #ff8c00;
                }
            """)

        add_btn.clicked.connect(self.add_product_db)
        update_btn.clicked.connect(self.update_product_db)
        delete_btn.clicked.connect(self.delete_product_db)

        button_layout.addWidget(add_btn)
        button_layout.addWidget(update_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addStretch()

        bottom_layout.addWidget(button_container, 1)

        main_layout.addLayout(bottom_layout)

        self._right_layout.addWidget(self._back_button, alignment=Qt.AlignLeft)
        self._right_layout.addWidget(main_container)
        self.current_panel = main_container

    def on_product_row_selected(self):
        if self.current_product_table.currentRow() >= 0:
            selected_row = self.current_product_table.currentRow()
            
            for col, field in enumerate(self.current_product_headers):
                cell_value = self.current_product_table.item(selected_row, col)
                if cell_value and field in self.product_inputs:
                    self.product_inputs[field].setText(cell_value.text())
                    # Clear any error states
                    if field in self.product_error_labels:
                        self.clear_field_error(self.product_inputs[field], self.product_error_labels[field])

    def filter_products_table(self):
        search_text = self.product_search_input.text().lower()
        
        if not search_text:
            filtered_data = self.all_product_data
        else:
            filtered_data = [
                row for row in self.all_product_data
                if any(search_text in str(value).lower() for value in row.values())
            ]
        
        parent_layout = self.current_product_table.parent().layout()
        index = parent_layout.indexOf(self.current_product_table)
        
        self.current_product_table.setParent(None)
        self.current_product_table = self.create_table(filtered_data, self.current_product_headers)
        self.current_product_table.itemSelectionChanged.connect(self.on_product_row_selected)
        parent_layout.insertWidget(index, self.current_product_table)

    def refresh_products_table(self):
        self.all_product_data = db.query("SELECT * FROM Products")
        self.product_search_input.clear()
        
        parent_layout = self.current_product_table.parent().layout()
        index = parent_layout.indexOf(self.current_product_table)
        
        self.current_product_table.setParent(None)
        self.current_product_table = self.create_table(self.all_product_data, self.current_product_headers)
        self.current_product_table.itemSelectionChanged.connect(self.on_product_row_selected)
        parent_layout.insertWidget(index, self.current_product_table)

    def clear_product_form(self):
        for field in self.product_inputs:
            self.product_inputs[field].clear()
            if field in self.product_error_labels:
                self.clear_field_error(self.product_inputs[field], self.product_error_labels[field])

    def add_product_db(self):
        # Clear all previous errors
        for field in self.product_error_labels:
            self.clear_field_error(self.product_inputs[field], self.product_error_labels[field])
        
        fields = ["product_name", "product_model", "product_color", "product_price", "product_stock", "stock_status"]
        values = [self.product_inputs[f].text() for f in fields]
        
        if not all(values):
            QMessageBox.warning(self, "Warning", "Please fill all fields.")
            return
        
        # Validate product name uniqueness
        has_error = False
        valid, error_msg = self.validate_product_name(values[0])
        if not valid:
            self.set_field_error(self.product_inputs["product_name"], 
                               self.product_error_labels["product_name"], error_msg)
            has_error = True
        
        if has_error:
            QMessageBox.warning(self, "Validation Error", "Please fix the errors highlighted in red.")
            return
        
        db.execute("INSERT INTO Products (product_name, product_model, product_color, product_price, product_stock, stock_status) VALUES (%s,%s,%s,%s,%s,%s)", values)
        QMessageBox.information(self, "Success", "Product added successfully.")
        self.refresh_products_table()
        self.clear_product_form()

    def update_product_db(self):
        product_id = self.product_inputs["product_id"].text()
        
        if not product_id:
            QMessageBox.warning(self, "Warning", "Please select a product to update.")
            return
        
        # Clear all previous errors
        for field in self.product_error_labels:
            self.clear_field_error(self.product_inputs[field], self.product_error_labels[field])
        
        fields = ["product_name", "product_model", "product_color", "product_price", "product_stock", "stock_status"]
        values = [self.product_inputs[f].text() for f in fields]
        
        if not all(values):
            QMessageBox.warning(self, "Warning", "Please fill all fields.")
            return
        
        # Validate product name uniqueness (excluding current record)
        has_error = False
        valid, error_msg = self.validate_product_name(values[0], product_id)
        if not valid:
            self.set_field_error(self.product_inputs["product_name"], 
                               self.product_error_labels["product_name"], error_msg)
            has_error = True
        
        if has_error:
            QMessageBox.warning(self, "Validation Error", "Please fix the errors highlighted in red.")
            return
        
        db.execute("UPDATE Products SET product_name=%s, product_model=%s, product_color=%s, product_price=%s, product_stock=%s, stock_status=%s WHERE product_id=%s",
                   (*values, product_id))
        QMessageBox.information(self, "Success", "Product updated successfully.")
        self.refresh_products_table()
        self.clear_product_form()

    def delete_product_db(self):
        product_id = self.product_inputs["product_id"].text()
        
        if not product_id:
            QMessageBox.warning(self, "Warning", "Please select a product to delete.")
            return
        
        reply = QMessageBox.question(self, "Confirm Delete", 
                                      f"Are you sure you want to delete product ID {product_id}?",
                                      QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            db.execute("DELETE FROM Products WHERE product_id=%s", (product_id,))
            QMessageBox.information(self, "Success", "Product deleted successfully.")
            self.refresh_products_table()
            self.clear_product_form()

    # HANDLE LOGOUT
    def handle_logout(self):
        reply = QMessageBox.question(
            self, 
            "Confirm Logout", 
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No  # Default button
        )
        
        if reply == QMessageBox.Yes:
            from main import MainWindow
            self.login_window = MainWindow()
            self.login_window.show()
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminWindow()
    window.show()
    sys.exit(app.exec_())