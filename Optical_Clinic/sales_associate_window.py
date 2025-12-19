import sys
import re
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import mysql.connector
from datetime import datetime
import os

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

    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.cursor.fetchall()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        self.connect_db.commit()
        
    def get_last_insert_id(self):
        return self.cursor.lastrowid

db = Database()

# SALES ASSOCIATE WINDOW
class SalesAssociateWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CJCEyeSite Management System | Sales Associate")
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
        self.all_data = []
        self.order_items = []  # For multi-product orders

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

        self.customers_button = QPushButton("CUSTOMERS")
        self.customers_button.setFont(button_font)
        self.customers_button.setStyleSheet("""
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
        self.customers_button.clicked.connect(self.show_customers_panel)
        layout.addWidget(self.customers_button)
        
        layout.addSpacing(15)

        self.appointments_button = QPushButton("APPOINTMENTS")
        self.appointments_button.setFont(button_font)
        self.appointments_button.setStyleSheet("""
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
        self.appointments_button.clicked.connect(self.show_appointments_panel)
        layout.addWidget(self.appointments_button)

        layout.addSpacing(15)

        self.orders_button = QPushButton("ORDERS")
        self.orders_button.setFont(button_font)
        self.orders_button.setStyleSheet("""
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
        self.orders_button.clicked.connect(self.show_orders_panel)
        layout.addWidget(self.orders_button)

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
        layout.addWidget(logout_button, alignment=Qt.AlignLeft)

    # RIGHT PANEL
    def init_right_panel(self):
        self._right_panel_widget = QWidget()
        self._right_panel_widget.setStyleSheet("background-color:#fffff0;")

        self._right_layout = QVBoxLayout(self._right_panel_widget)
        self._right_layout.setContentsMargins(12, 12, 12, 12)

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
            "customer_id": "Customer ID",
            "customer_name": "Customer Name",
            "customer_cnum": "Contact Number",
            "customer_email": "Email Address",
            "appointment_id": "Appointment ID",
            "employee_id": "Employee ID",
            "appointment_date": "Date",
            "appointment_time": "Time",
            "order_id": "Order ID",
            "product_id": "Product ID",
            "product_name": "Product Name",
            "product_model": "Model",
            "product_color": "Color",
            "product_price": "Price",
            "product_stock": "Stock Quantity",
            "stock_status": "Stock Status",
            "order_quantity": "Quantity",
            "order_status": "Order Status",
        }
        return mapping.get(field, field.replace("_", " ").title())

    # VALIDATION METHODS
    def validate_email(self, email):
        """Validate email format"""
        if not email:
            return False, "Email cannot be empty"
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "Invalid email format"
        return True, ""

    def validate_contact_number(self, number):
        """Validate Philippine contact number"""
        if not number:
            return False, "Contact number cannot be empty"
        
        # Remove spaces and dashes
        clean_number = number.replace(" ", "").replace("-", "")
        
        # Check if it's digits only
        if not clean_number.isdigit():
            return False, "Contact number must contain only digits"
        
        # Philippine numbers: 09XXXXXXXXX or +639XXXXXXXXX or 639XXXXXXXXX
        if len(clean_number) == 11 and clean_number.startswith("09"):
            return True, ""
        elif len(clean_number) == 12 and clean_number.startswith("639"):
            return True, ""
        elif len(clean_number) == 13 and clean_number.startswith("+639"):
            return True, ""
        else:
            return False, "Invalid Philippine number format (e.g., 09XXXXXXXXX)"

    def validate_customer_id_exists(self, customer_id):
        """Check if customer ID exists in database"""
        if not customer_id:
            return False, "Customer ID cannot be empty"
        
        try:
            customer_id_int = int(customer_id)
        except ValueError:
            return False, "Customer ID must be a number"
        
        result = db.query("SELECT customer_id FROM Customers WHERE customer_id=%s", (customer_id_int,))
        if not result:
            return False, "Customer ID does not exist"
        return True, ""

    def validate_employee_id_exists(self, employee_id):
        """Check if employee ID exists in database"""
        if not employee_id:
            return False, "Employee ID cannot be empty"
        
        try:
            employee_id_int = int(employee_id)
        except ValueError:
            return False, "Employee ID must be a number"
        
        result = db.query("SELECT employee_id FROM Employees WHERE employee_id=%s", (employee_id_int,))
        if not result:
            return False, "Employee ID does not exist"
        return True, ""

    def validate_product_id_exists(self, product_id):
        """Check if product ID exists in database"""
        if not product_id:
            return False, "Product ID cannot be empty"
        
        try:
            product_id_int = int(product_id)
        except ValueError:
            return False, "Product ID must be a number"
        
        result = db.query("SELECT product_id FROM Products WHERE product_id=%s", (product_id_int,))
        if not result:
            return False, "Product ID does not exist"
        return True, ""

    def validate_order_quantity(self, quantity, product_id=None):
        """Validate order quantity"""
        if not quantity:
            return False, "Quantity cannot be empty"
        
        try:
            qty_int = int(quantity)
        except ValueError:
            return False, "Quantity must be a number"
        
        if qty_int <= 0:
            return False, "Quantity must be greater than 0"
        
        # Check stock if product_id is provided
        if product_id:
            try:
                product = db.query("SELECT product_stock FROM Products WHERE product_id=%s", (product_id,))
                if product and qty_int > product[0]['product_stock']:
                    return False, f"Not enough stock (Available: {product[0]['product_stock']})"
            except:
                pass
        
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

    # ==================== CUSTOMERS PANEL ====================
    def show_customers_panel(self):
        self.save_current_panel()
        self.clear_right_panel()

        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(20, 20, 20, 20)

        header_layout = QHBoxLayout()
        
        title_label = QLabel("Customers")
        title_label.setFont(QFont("Futura Cyrillic Medium", 20, QFont.Bold))
        title_label.setStyleSheet("color: #373737;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

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
        self.search_input.textChanged.connect(self.filter_customers_table)
        header_layout.addWidget(self.search_input)

        main_layout.addLayout(header_layout)
        main_layout.addSpacing(15)

        self.all_data = db.query("SELECT * FROM Customers")
        self.current_headers = ["customer_id", "customer_name", "customer_cnum", "customer_email"]
        
        self.current_table_widget = self.create_table(self.all_data, self.current_headers)
        self.current_table_widget.itemSelectionChanged.connect(self.on_customer_row_selected)
        
        main_layout.addWidget(self.current_table_widget)

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)

        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 10, 0, 0)

        form_grid = QGridLayout()
        form_grid.setHorizontalSpacing(15)
        form_grid.setVerticalSpacing(10)

        fields = ["customer_id", "customer_name", "customer_cnum", "customer_email"]
        self.customer_inputs = {}
        self.customer_error_labels = {}

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
            
            if field == "customer_id":
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
            
            self.customer_inputs[field] = line_edit
            self.customer_error_labels[field] = error_label

        form_layout.addLayout(form_grid)
        form_layout.addStretch()
        bottom_layout.addWidget(form_container, 3)

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

        add_btn.clicked.connect(self.add_customer_db)
        update_btn.clicked.connect(self.update_customer_db)
        delete_btn.clicked.connect(self.delete_customer_db)

        button_layout.addWidget(add_btn)
        button_layout.addWidget(update_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addStretch()

        bottom_layout.addWidget(button_container, 1)
        main_layout.addLayout(bottom_layout)

        self._right_layout.addWidget(self._back_button, alignment=Qt.AlignLeft)
        self._right_layout.addWidget(main_container)
        self.current_panel = main_container

    def on_customer_row_selected(self):
        if self.current_table_widget.currentRow() >= 0:
            selected_row = self.current_table_widget.currentRow()
            for col, field in enumerate(self.current_headers):
                cell_value = self.current_table_widget.item(selected_row, col)
                if cell_value and field in self.customer_inputs:
                    self.customer_inputs[field].setText(cell_value.text())
            
            # Clear any error states
            for field in self.customer_error_labels:
                self.clear_field_error(self.customer_inputs[field], self.customer_error_labels[field])

    def filter_customers_table(self):
        search_text = self.search_input.text().lower()
        filtered_data = self.all_data if not search_text else [
            row for row in self.all_data
            if any(search_text in str(value).lower() for value in row.values())
        ]
        
        parent_layout = self.current_table_widget.parent().layout()
        index = parent_layout.indexOf(self.current_table_widget)
        self.current_table_widget.setParent(None)
        self.current_table_widget = self.create_table(filtered_data, self.current_headers)
        self.current_table_widget.itemSelectionChanged.connect(self.on_customer_row_selected)
        parent_layout.insertWidget(index, self.current_table_widget)

    def refresh_customers_table(self):
        self.all_data = db.query("SELECT * FROM Customers")
        self.search_input.clear()
        parent_layout = self.current_table_widget.parent().layout()
        index = parent_layout.indexOf(self.current_table_widget)
        self.current_table_widget.setParent(None)
        self.current_table_widget = self.create_table(self.all_data, self.current_headers)
        self.current_table_widget.itemSelectionChanged.connect(self.on_customer_row_selected)
        parent_layout.insertWidget(index, self.current_table_widget)

    def clear_customer_form(self):
        for field in self.customer_inputs:
            self.customer_inputs[field].clear()
            if field in self.customer_error_labels:
                self.clear_field_error(self.customer_inputs[field], self.customer_error_labels[field])

    def add_customer_db(self):
        # Clear all previous errors
        for field in self.customer_error_labels:
            self.clear_field_error(self.customer_inputs[field], self.customer_error_labels[field])
        
        fields = ["customer_name", "customer_cnum", "customer_email"]
        values = [self.customer_inputs[f].text() for f in fields]
        
        if not all(values):
            QMessageBox.warning(self, "Warning", "Please fill all fields.")
            return
        
        # Validate each field
        has_error = False
        
        # Validate contact number
        valid, error_msg = self.validate_contact_number(values[1])
        if not valid:
            self.set_field_error(self.customer_inputs["customer_cnum"], 
                               self.customer_error_labels["customer_cnum"], error_msg)
            has_error = True
        
        # Validate email
        valid, error_msg = self.validate_email(values[2])
        if not valid:
            self.set_field_error(self.customer_inputs["customer_email"], 
                               self.customer_error_labels["customer_email"], error_msg)
            has_error = True
        
        if has_error:
            QMessageBox.warning(self, "Validation Error", "Please fix the errors highlighted in red.")
            return
        
        db.execute("INSERT INTO Customers (customer_name, customer_cnum, customer_email) VALUES (%s,%s,%s)", values)
        QMessageBox.information(self, "Success", "Customer added successfully.")
        self.refresh_customers_table()
        self.clear_customer_form()

    def update_customer_db(self):
        customer_id = self.customer_inputs["customer_id"].text()
        if not customer_id:
            QMessageBox.warning(self, "Warning", "Please select a customer to update.")
            return
        
        # Clear all previous errors
        for field in self.customer_error_labels:
            self.clear_field_error(self.customer_inputs[field], self.customer_error_labels[field])
        
        fields = ["customer_name", "customer_cnum", "customer_email"]
        values = [self.customer_inputs[f].text() for f in fields]
        
        if not all(values):
            QMessageBox.warning(self, "Warning", "Please fill all fields.")
            return
        
        # Validate each field
        has_error = False
        
        # Validate contact number
        valid, error_msg = self.validate_contact_number(values[1])
        if not valid:
            self.set_field_error(self.customer_inputs["customer_cnum"], 
                               self.customer_error_labels["customer_cnum"], error_msg)
            has_error = True
        
        # Validate email
        valid, error_msg = self.validate_email(values[2])
        if not valid:
            self.set_field_error(self.customer_inputs["customer_email"], 
                               self.customer_error_labels["customer_email"], error_msg)
            has_error = True
        
        if has_error:
            QMessageBox.warning(self, "Validation Error", "Please fix the errors highlighted in red.")
            return
        
        db.execute("UPDATE Customers SET customer_name=%s, customer_cnum=%s, customer_email=%s WHERE customer_id=%s",
                   (*values, customer_id))
        QMessageBox.information(self, "Success", "Customer updated successfully.")
        self.refresh_customers_table()
        self.clear_customer_form()

    def delete_customer_db(self):
        customer_id = self.customer_inputs["customer_id"].text()
        if not customer_id:
            QMessageBox.warning(self, "Warning", "Please select a customer to delete.")
            return
        reply = QMessageBox.question(self, "Confirm Delete", 
                                      f"Are you sure you want to delete customer ID {customer_id}?",
                                      QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            db.execute("DELETE FROM Customers WHERE customer_id=%s", (customer_id,))
            QMessageBox.information(self, "Success", "Customer deleted successfully.")
            self.refresh_customers_table()
            self.clear_customer_form()

    # ==================== APPOINTMENTS PANEL ====================
    def show_appointments_panel(self):
        self.save_current_panel()
        self.clear_right_panel()

        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(20, 20, 20, 20)

        header_layout = QHBoxLayout()
        title_label = QLabel("Appointments")
        title_label.setFont(QFont("Futura Cyrillic Medium", 20, QFont.Bold))
        title_label.setStyleSheet("color: #373737;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        self.appt_search_input = QLineEdit()
        self.appt_search_input.setPlaceholderText("Search...")
        self.appt_search_input.setFixedSize(250, 35)
        self.appt_search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #f69623;
                border-radius: 5px;
                padding: 5px 10px;
                background-color: white;
            }
        """)
        self.appt_search_input.textChanged.connect(self.filter_appointments_table)
        header_layout.addWidget(self.appt_search_input)

        main_layout.addLayout(header_layout)
        main_layout.addSpacing(15)

        self.all_appt_data = db.query("SELECT * FROM Appointments")
        self.current_appt_headers = ["appointment_id", "customer_id", "employee_id", "appointment_date", "appointment_time"]
        
        self.current_appt_table = self.create_table(self.all_appt_data, self.current_appt_headers)
        self.current_appt_table.itemSelectionChanged.connect(self.on_appointment_row_selected)
        main_layout.addWidget(self.current_appt_table)

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)

        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 10, 0, 0)

        form_grid = QGridLayout()
        form_grid.setHorizontalSpacing(15)
        form_grid.setVerticalSpacing(10)

        fields = ["appointment_id", "customer_id", "employee_id", "appointment_date", "appointment_time"]
        self.appointment_inputs = {}
        self.appointment_error_labels = {}

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
            
            if field == "appointment_id":
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
            
            self.appointment_inputs[field] = line_edit
            self.appointment_error_labels[field] = error_label

        form_layout.addLayout(form_grid)
        form_layout.addStretch()
        bottom_layout.addWidget(form_container, 3)

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

        add_btn.clicked.connect(self.add_appointment_db)
        update_btn.clicked.connect(self.update_appointment_db)
        delete_btn.clicked.connect(self.delete_appointment_db)

        button_layout.addWidget(add_btn)
        button_layout.addWidget(update_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addStretch()

        bottom_layout.addWidget(button_container, 1)
        main_layout.addLayout(bottom_layout)

        self._right_layout.addWidget(self._back_button, alignment=Qt.AlignLeft)
        self._right_layout.addWidget(main_container)
        self.current_panel = main_container

    def on_appointment_row_selected(self):
        if self.current_appt_table.currentRow() >= 0:
            selected_row = self.current_appt_table.currentRow()
            for col, field in enumerate(self.current_appt_headers):
                cell_value = self.current_appt_table.item(selected_row, col)
                if cell_value and field in self.appointment_inputs:
                    self.appointment_inputs[field].setText(cell_value.text())
            
            # Clear any error states
            for field in self.appointment_error_labels:
                self.clear_field_error(self.appointment_inputs[field], self.appointment_error_labels[field])

    def filter_appointments_table(self):
        search_text = self.appt_search_input.text().lower()
        filtered_data = self.all_appt_data if not search_text else [
            row for row in self.all_appt_data
            if any(search_text in str(value).lower() for value in row.values())
        ]
        
        parent_layout = self.current_appt_table.parent().layout()
        index = parent_layout.indexOf(self.current_appt_table)
        self.current_appt_table.setParent(None)
        self.current_appt_table = self.create_table(filtered_data, self.current_appt_headers)
        self.current_appt_table.itemSelectionChanged.connect(self.on_appointment_row_selected)
        parent_layout.insertWidget(index, self.current_appt_table)

    def refresh_appointments_table(self):
        self.all_appt_data = db.query("SELECT * FROM Appointments")
        self.appt_search_input.clear()
        parent_layout = self.current_appt_table.parent().layout()
        index = parent_layout.indexOf(self.current_appt_table)
        self.current_appt_table.setParent(None)
        self.current_appt_table = self.create_table(self.all_appt_data, self.current_appt_headers)
        self.current_appt_table.itemSelectionChanged.connect(self.on_appointment_row_selected)
        parent_layout.insertWidget(index, self.current_appt_table)

    def clear_appointment_form(self):
        for field in self.appointment_inputs:
            self.appointment_inputs[field].clear()
            if field in self.appointment_error_labels:
                self.clear_field_error(self.appointment_inputs[field], self.appointment_error_labels[field])

    def add_appointment_db(self):
        # Clear all previous errors
        for field in self.appointment_error_labels:
            self.clear_field_error(self.appointment_inputs[field], self.appointment_error_labels[field])
        
        fields = ["customer_id", "employee_id", "appointment_date", "appointment_time"]
        values = [self.appointment_inputs[f].text() for f in fields]
        
        if not all(values):
            QMessageBox.warning(self, "Warning", "Please fill all fields.")
            return
        
        # Validate each field
        has_error = False
        
        # Validate customer_id exists
        valid, error_msg = self.validate_customer_id_exists(values[0])
        if not valid:
            self.set_field_error(self.appointment_inputs["customer_id"], 
                               self.appointment_error_labels["customer_id"], error_msg)
            has_error = True
        
        # Validate employee_id exists
        valid, error_msg = self.validate_employee_id_exists(values[1])
        if not valid:
            self.set_field_error(self.appointment_inputs["employee_id"], 
                               self.appointment_error_labels["employee_id"], error_msg)
            has_error = True
        
        if has_error:
            QMessageBox.warning(self, "Validation Error", "Please fix the errors highlighted in red.")
            return
        
        db.execute("INSERT INTO Appointments (customer_id, employee_id, appointment_date, appointment_time) VALUES (%s,%s,%s,%s)", values)
        QMessageBox.information(self, "Success", "Appointment added successfully.")
        self.refresh_appointments_table()
        self.clear_appointment_form()

    def update_appointment_db(self):
        appointment_id = self.appointment_inputs["appointment_id"].text()
        if not appointment_id:
            QMessageBox.warning(self, "Warning", "Please select an appointment to update.")
            return
        
        # Clear all previous errors
        for field in self.appointment_error_labels:
            self.clear_field_error(self.appointment_inputs[field], self.appointment_error_labels[field])
        
        fields = ["customer_id", "employee_id", "appointment_date", "appointment_time"]
        values = [self.appointment_inputs[f].text() for f in fields]
        
        if not all(values):
            QMessageBox.warning(self, "Warning", "Please fill all fields.")
            return
        
        # Validate each field
        has_error = False
        
        # Validate customer_id exists
        valid, error_msg = self.validate_customer_id_exists(values[0])
        if not valid:
            self.set_field_error(self.appointment_inputs["customer_id"], 
                               self.appointment_error_labels["customer_id"], error_msg)
            has_error = True
        
        # Validate employee_id exists
        valid, error_msg = self.validate_employee_id_exists(values[1])
        if not valid:
            self.set_field_error(self.appointment_inputs["employee_id"], 
                               self.appointment_error_labels["employee_id"], error_msg)
            has_error = True
        
        if has_error:
            QMessageBox.warning(self, "Validation Error", "Please fix the errors highlighted in red.")
            return
        
        db.execute("UPDATE Appointments SET customer_id=%s, employee_id=%s, appointment_date=%s, appointment_time=%s WHERE appointment_id=%s",
                   (*values, appointment_id))
        QMessageBox.information(self, "Success", "Appointment updated successfully.")
        self.refresh_appointments_table()
        self.clear_appointment_form()

    def delete_appointment_db(self):
        appointment_id = self.appointment_inputs["appointment_id"].text()
        if not appointment_id:
            QMessageBox.warning(self, "Warning", "Please select an appointment to delete.")
            return
        reply = QMessageBox.question(self, "Confirm Delete", 
                                      f"Are you sure you want to delete appointment ID {appointment_id}?",
                                      QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            db.execute("DELETE FROM Appointments WHERE appointment_id=%s", (appointment_id,))
            QMessageBox.information(self, "Success", "Appointment deleted successfully.")
            self.refresh_appointments_table()
            self.clear_appointment_form()

    # ==================== ORDERS PANEL ====================
    def show_orders_panel(self):
        self.save_current_panel()
        self.clear_right_panel()

        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(20, 20, 20, 20)

        header_layout = QHBoxLayout()
        title_label = QLabel("Orders")
        title_label.setFont(QFont("Futura Cyrillic Medium", 20, QFont.Bold))
        title_label.setStyleSheet("color: #373737;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        # Create New Order Button
        new_order_btn = QPushButton("+ Create New Order")
        new_order_btn.setFixedSize(180, 40)
        new_order_btn.setFont(QFont("Futura Cyrillic Medium", 11))
        new_order_btn.setStyleSheet("""
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
        new_order_btn.clicked.connect(self.show_create_order_dialog)
        header_layout.addWidget(new_order_btn)

        main_layout.addLayout(header_layout)
        main_layout.addSpacing(15)

        self.all_order_data = db.query("SELECT * FROM Orders")
        self.current_order_headers = ["order_id", "product_id", "customer_id", "order_quantity", "order_status"]
        
        self.current_order_table = self.create_table(self.all_order_data, self.current_order_headers)
        self.current_order_table.itemSelectionChanged.connect(self.on_order_row_selected)
        main_layout.addWidget(self.current_order_table)

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)

        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 10, 0, 0)

        form_grid = QGridLayout()
        form_grid.setHorizontalSpacing(15)
        form_grid.setVerticalSpacing(10)

        fields = ["order_id", "product_id", "customer_id", "order_quantity", "order_status"]
        self.order_inputs = {}
        self.order_error_labels = {}

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
            
            if field == "order_id":
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
            
            self.order_inputs[field] = line_edit
            self.order_error_labels[field] = error_label

        form_layout.addLayout(form_grid)
        form_layout.addStretch()
        bottom_layout.addWidget(form_container, 3)

        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setContentsMargins(0, 10, 0, 0)
        button_layout.setSpacing(10)

        update_btn = QPushButton("Update")
        delete_btn = QPushButton("Delete")

        for btn in [update_btn, delete_btn]:
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

        update_btn.clicked.connect(self.update_order_db)
        delete_btn.clicked.connect(self.delete_order_db)

        button_layout.addWidget(update_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addStretch()

        bottom_layout.addWidget(button_container, 1)
        main_layout.addLayout(bottom_layout)

        self._right_layout.addWidget(self._back_button, alignment=Qt.AlignLeft)
        self._right_layout.addWidget(main_container)
        self.current_panel = main_container

    def on_order_row_selected(self):
        if self.current_order_table.currentRow() >= 0:
            selected_row = self.current_order_table.currentRow()
            for col, field in enumerate(self.current_order_headers):
                cell_value = self.current_order_table.item(selected_row, col)
                if cell_value and field in self.order_inputs:
                    self.order_inputs[field].setText(cell_value.text())
            
            # Clear any error states
            for field in self.order_error_labels:
                self.clear_field_error(self.order_inputs[field], self.order_error_labels[field])

    def refresh_orders_table(self):
        self.all_order_data = db.query("SELECT * FROM Orders")
        parent_layout = self.current_order_table.parent().layout()
        index = parent_layout.indexOf(self.current_order_table)
        self.current_order_table.setParent(None)
        self.current_order_table = self.create_table(self.all_order_data, self.current_order_headers)
        self.current_order_table.itemSelectionChanged.connect(self.on_order_row_selected)
        parent_layout.insertWidget(index, self.current_order_table)

    def clear_order_form(self):
        for field in self.order_inputs:
            self.order_inputs[field].clear()
            if field in self.order_error_labels:
                self.clear_field_error(self.order_inputs[field], self.order_error_labels[field])

    def update_order_db(self):
        order_id = self.order_inputs["order_id"].text()
        if not order_id:
            QMessageBox.warning(self, "Warning", "Please select an order to update.")
            return
        
        # Clear all previous errors
        for field in self.order_error_labels:
            self.clear_field_error(self.order_inputs[field], self.order_error_labels[field])
        
        fields = ["product_id", "customer_id", "order_quantity", "order_status"]
        values = [self.order_inputs[f].text() for f in fields]
        
        if not all(values):
            QMessageBox.warning(self, "Warning", "Please fill all fields.")
            return
        
        # Validate each field
        has_error = False
        
        # Validate product_id exists
        valid, error_msg = self.validate_product_id_exists(values[0])
        if not valid:
            self.set_field_error(self.order_inputs["product_id"], 
                               self.order_error_labels["product_id"], error_msg)
            has_error = True
        
        # Validate customer_id exists
        valid, error_msg = self.validate_customer_id_exists(values[1])
        if not valid:
            self.set_field_error(self.order_inputs["customer_id"], 
                               self.order_error_labels["customer_id"], error_msg)
            has_error = True
        
        # Validate order quantity
        valid, error_msg = self.validate_order_quantity(values[2], values[0])
        if not valid:
            self.set_field_error(self.order_inputs["order_quantity"], 
                               self.order_error_labels["order_quantity"], error_msg)
            has_error = True
        
        if has_error:
            QMessageBox.warning(self, "Validation Error", "Please fix the errors highlighted in red.")
            return
        
        db.execute("UPDATE Orders SET product_id=%s, customer_id=%s, order_quantity=%s, order_status=%s WHERE order_id=%s",
                   (*values, order_id))
        QMessageBox.information(self, "Success", "Order updated successfully.")
        self.refresh_orders_table()
        self.clear_order_form()

    def delete_order_db(self):
        order_id = self.order_inputs["order_id"].text()
        if not order_id:
            QMessageBox.warning(self, "Warning", "Please select an order to delete.")
            return
        reply = QMessageBox.question(self, "Confirm Delete", 
                                      f"Are you sure you want to delete order ID {order_id}?",
                                      QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            db.execute("DELETE FROM Orders WHERE order_id=%s", (order_id,))
            QMessageBox.information(self, "Success", "Order deleted successfully.")
            self.refresh_orders_table()
            self.clear_order_form()

    # ==================== CREATE ORDER DIALOG (Multi-Product) ====================
    def show_create_order_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Create New Order")
        dialog.setFixedSize(700, 600)
        dialog.setStyleSheet("background-color: #fffff0;")

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(30, 30, 30, 30)

        title_label = QLabel("Create New Order")
        title_label.setFont(QFont("Futura Cyrillic Medium", 18, QFont.Bold))
        title_label.setStyleSheet("color: #f69623;")
        layout.addWidget(title_label)
        layout.addSpacing(20)

        # Customer ID input
        customer_layout = QHBoxLayout()
        customer_label = QLabel("Customer ID:")
        customer_label.setFont(QFont("Futura Cyrillic Medium", 11))
        self.dialog_customer_id = QLineEdit()
        self.dialog_customer_id.setFixedHeight(30)
        self.dialog_customer_id.setStyleSheet("background-color: white; border: 1px solid #d9d9d9; padding: 5px;")
        customer_layout.addWidget(customer_label)
        customer_layout.addWidget(self.dialog_customer_id)
        layout.addLayout(customer_layout)
        layout.addSpacing(15)

        # Order items section
        items_label = QLabel("Order Items:")
        items_label.setFont(QFont("Futura Cyrillic Medium", 12, QFont.Bold))
        layout.addWidget(items_label)

        # Table for order items
        self.order_items = []
        self.order_items_table = QTableWidget(0, 4)
        self.order_items_table.setHorizontalHeaderLabels(["Product ID", "Product Name", "Quantity", "Remove"])
        self.order_items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.order_items_table.setMaximumHeight(200)
        self.order_items_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #f69623;
                color: white;
                padding: 5px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.order_items_table)
        layout.addSpacing(10)

        # Add product section
        add_product_layout = QHBoxLayout()
        
        product_label = QLabel("Product ID:")
        self.dialog_product_id = QLineEdit()
        self.dialog_product_id.setFixedWidth(100)
        self.dialog_product_id.setStyleSheet("background-color: white; border: 1px solid #d9d9d9; padding: 5px;")
        
        qty_label = QLabel("Quantity:")
        self.dialog_quantity = QLineEdit()
        self.dialog_quantity.setFixedWidth(80)
        self.dialog_quantity.setStyleSheet("background-color: white; border: 1px solid #d9d9d9; padding: 5px;")
        
        add_product_btn = QPushButton("+ Add Product")
        add_product_btn.setFixedSize(130, 35)
        add_product_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        add_product_btn.clicked.connect(self.add_product_to_order)
        
        add_product_layout.addWidget(product_label)
        add_product_layout.addWidget(self.dialog_product_id)
        add_product_layout.addWidget(qty_label)
        add_product_layout.addWidget(self.dialog_quantity)
        add_product_layout.addWidget(add_product_btn)
        add_product_layout.addStretch()
        
        layout.addLayout(add_product_layout)
        layout.addSpacing(20)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        create_btn = QPushButton("Create Order")
        
        for btn in [cancel_btn, create_btn]:
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
        
        cancel_btn.clicked.connect(dialog.reject)
        create_btn.clicked.connect(lambda: self.create_multi_product_order(dialog))
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(create_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec_()

    def add_product_to_order(self):
        product_id = self.dialog_product_id.text().strip()
        quantity = self.dialog_quantity.text().strip()
        
        if not product_id or not quantity:
            QMessageBox.warning(self, "Warning", "Please enter Product ID and Quantity.")
            return
        
        # Validate product_id exists
        valid, error_msg = self.validate_product_id_exists(product_id)
        if not valid:
            QMessageBox.warning(self, "Warning", error_msg)
            return
        
        # Validate quantity
        valid, error_msg = self.validate_order_quantity(quantity)
        if not valid:
            QMessageBox.warning(self, "Warning", error_msg)
            return
        
        quantity = int(quantity)
        
        # Fetch product details
        product = db.query("SELECT product_name, product_stock FROM Products WHERE product_id=%s", (product_id,))
        if not product:
            QMessageBox.warning(self, "Warning", f"Product ID {product_id} not found.")
            return
        
        product = product[0]
        if quantity > product['product_stock']:
            QMessageBox.warning(self, "Warning", f"Not enough stock. Available: {product['product_stock']}")
            return
        
        # Add to order items
        self.order_items.append({
            'product_id': product_id,
            'product_name': product['product_name'],
            'quantity': quantity
        })
        
        # Update table
        row = self.order_items_table.rowCount()
        self.order_items_table.insertRow(row)
        self.order_items_table.setItem(row, 0, QTableWidgetItem(product_id))
        self.order_items_table.setItem(row, 1, QTableWidgetItem(product['product_name']))
        self.order_items_table.setItem(row, 2, QTableWidgetItem(str(quantity)))
        
        # Remove button
        remove_btn = QPushButton("Remove")
        remove_btn.setStyleSheet("background-color: #f44336; color: white; border: none; padding: 5px;")
        remove_btn.clicked.connect(lambda: self.remove_product_from_order(row))
        self.order_items_table.setCellWidget(row, 3, remove_btn)
        
        # Clear inputs
        self.dialog_product_id.clear()
        self.dialog_quantity.clear()

    def remove_product_from_order(self, row):
        self.order_items_table.removeRow(row)
        if row < len(self.order_items):
            self.order_items.pop(row)

    def create_multi_product_order(self, dialog):
        customer_id = self.dialog_customer_id.text().strip()
        
        if not customer_id:
            QMessageBox.warning(self, "Warning", "Please enter Customer ID.")
            return
        
        # Validate customer_id exists
        valid, error_msg = self.validate_customer_id_exists(customer_id)
        if not valid:
            QMessageBox.warning(self, "Warning", error_msg)
            return
        
        if not self.order_items:
            QMessageBox.warning(self, "Warning", "Please add at least one product to the order.")
            return
        
        # Insert each product as a separate order
        for item in self.order_items:
            # Update stock
            db.execute("UPDATE Products SET product_stock = product_stock - %s WHERE product_id=%s",
                      (item['quantity'], item['product_id']))
            
            # Insert order
            db.execute("INSERT INTO Orders (product_id, customer_id, order_quantity, order_status) VALUES (%s,%s,%s,'Pending')",
                      (item['product_id'], customer_id, item['quantity']))
            
            # Create receipt for this order
            order_id = db.get_last_insert_id()
            self.create_receipt(order_id)
        
        QMessageBox.information(self, "Success", f"Order created successfully with {len(self.order_items)} products!")
        self.order_items = []
        dialog.accept()
        self.refresh_orders_table()

    # ==================== CREATE RECEIPT ====================
    def create_receipt(self, order_id):
        order = db.query("""
            SELECT o.order_id, o.order_status, o.order_quantity, c.customer_name,
                   p.product_name, p.product_model, p.product_color, p.product_price
            FROM Orders o
            JOIN Customers c ON o.customer_id = c.customer_id
            JOIN Products p ON o.product_id = p.product_id
            WHERE o.order_id=%s
        """, (order_id,))
        
        if not order:
            return
        
        order = order[0]
        receipts_dir = "C:/Users/Ianne/Programming/Projects/Python/Optical_Clinic/Receipts"
        os.makedirs(receipts_dir, exist_ok=True)
        filename = f"EyeSite_Receipt_{order['order_id']}.txt"
        filepath = os.path.join(receipts_dir, filename)
        total_amount = order['order_quantity'] * order['product_price']
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("===== CJCEyeSite Optical Clinic =====\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Order ID: {order['order_id']}\n")
            f.write(f"Customer Name: {order['customer_name']}\n")
            f.write("========================================\n")
            f.write(f"{'Product':20} {'Model':12} {'Color':10} {'Qty':5} {'Price':12} {'Total':12}\n")
            f.write("----------------------------------------\n")
            f.write(f"{order['product_name'][:20]:20} {order['product_model'][:12]:12} {order['product_color'][:10]:10} {order['order_quantity']:<5} ₱{order['product_price']:10.2f} ₱{total_amount:10.2f}\n")
            f.write("----------------------------------------\n")
            f.write(f"Order Status: {order['order_status']}\n")
            f.write("========================================\n")

    # ==================== PRODUCTS PANEL ====================
    def show_products_panel(self):
        self.save_current_panel()
        self.clear_right_panel()
        
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel("Products (View Only)")
        title_label.setFont(QFont("Futura Cyrillic Medium", 20, QFont.Bold))
        title_label.setStyleSheet("color: #373737;")
        main_layout.addWidget(title_label)
        main_layout.addSpacing(15)
        
        data = db.query("SELECT * FROM Products")
        headers = ["product_id", "product_name", "product_model", "product_color", "product_price", "product_stock"]
        table = self.create_table(data, headers)
        table.setMaximumHeight(1000)
        main_layout.addWidget(table)
        
        self._right_layout.addWidget(self._back_button, alignment=Qt.AlignLeft)
        self._right_layout.addWidget(main_container)
        self.current_panel = main_container

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
    window = SalesAssociateWindow()
    window.show()
    sys.exit(app.exec_())