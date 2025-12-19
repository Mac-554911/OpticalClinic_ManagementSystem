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

    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.cursor.fetchall()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        self.connect_db.commit()

db = Database()

# OPTOMETRIST WINDOW
class OptometristWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CJCEyeSite Management System | Optometrist")
        self.setWindowIcon(QIcon(r"C:/Users/Ianne/Programming/Projects/Python/Optical_Clinic/Icons/eyesite_orange_logo.png"))
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowMinimizeButtonHint |
            Qt.WindowCloseButtonHint
        )
        self.panel_history = []
        self.current_panel = None
        self.current_table_widget = None
        self.all_data = []
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

        self.schedule_button = QPushButton("SCHEDULE")
        self.schedule_button.setFont(button_font)
        self.schedule_button.setStyleSheet("""
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
        self.schedule_button.clicked.connect(self.show_schedule_panel)
        layout.addWidget(self.schedule_button)
        layout.addSpacing(15)

        self.patient_button = QPushButton("PATIENT")
        self.patient_button.setFont(button_font)
        self.patient_button.setStyleSheet("""
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
        self.patient_button.clicked.connect(self.show_patient_panel)
        layout.addWidget(self.patient_button)
        layout.addSpacing(15)

        self.prescription_button = QPushButton("PRESCRIPTION")
        self.prescription_button.setFont(button_font)
        self.prescription_button.setStyleSheet("""
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
        self.prescription_button.clicked.connect(self.show_prescription_panel)
        layout.addWidget(self.prescription_button)

        layout.addStretch()

        # LOGOUT
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
            "appointment_id": "Appointment ID",
            "customer_name": "Customer Name",
            "appointment_date": "Date",
            "appointment_time": "Time",
            "customer_id": "Customer ID",
            "customer_cnum": "Contact Number",
            "customer_email": "Email Address",
            "prescription_id": "Prescription ID",
            "prescription_notes": "Prescription Notes"
        }
        return mapping.get(field, field.replace("_", " ").title())

    # VALIDATION METHODS
    def validate_customer_id_exists(self, customer_id):
        """Check if customer ID exists in database"""
        if not customer_id:
            return False, ""
        
        try:
            customer_id_int = int(customer_id)
        except ValueError:
            return False, "Customer ID must be a number"
        
        result = db.query("SELECT customer_id FROM Customers WHERE customer_id=%s", (customer_id_int,))
        if not result:
            return False, "Customer ID does not exist"
        return True, ""

    def validate_prescription_notes(self, notes):
        """Validate prescription notes"""
        if not notes:
            return False, "Prescription notes cannot be empty"
        
        if len(notes.strip()) < 5:
            return False, "Prescription notes must be at least 5 characters"
        
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

    # ==================== SCHEDULE PANEL ====================
    def show_schedule_panel(self):
        self.save_current_panel()
        self.clear_right_panel()

        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(20, 20, 20, 20)

        header_layout = QHBoxLayout()
        
        title_label = QLabel("Schedule")
        title_label.setFont(QFont("Futura Cyrillic Medium", 20, QFont.Bold))
        title_label.setStyleSheet("color: #373737;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        self.schedule_search_input = QLineEdit()
        self.schedule_search_input.setPlaceholderText("Search...")
        self.schedule_search_input.setFixedSize(250, 35)
        self.schedule_search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #f69623;
                border-radius: 5px;
                padding: 5px 10px;
                background-color: white;
            }
        """)
        self.schedule_search_input.textChanged.connect(self.filter_schedule_table)
        header_layout.addWidget(self.schedule_search_input)

        main_layout.addLayout(header_layout)
        main_layout.addSpacing(15)

        self.all_schedule_data = db.query("""
            SELECT a.appointment_id, c.customer_name, a.appointment_date, a.appointment_time
            FROM Appointments a
            JOIN Customers c ON a.customer_id = c.customer_id
        """)
        self.current_schedule_headers = ["appointment_id", "customer_name", "appointment_date", "appointment_time"]
        
        self.current_schedule_table = self.create_table(self.all_schedule_data, self.current_schedule_headers)
        main_layout.addWidget(self.current_schedule_table)

        self._right_layout.addWidget(self._back_button, alignment=Qt.AlignLeft)
        self._right_layout.addWidget(main_container)
        self.current_panel = main_container

    def filter_schedule_table(self):
        search_text = self.schedule_search_input.text().lower()
        filtered_data = self.all_schedule_data if not search_text else [
            row for row in self.all_schedule_data
            if any(search_text in str(value).lower() for value in row.values())
        ]
        
        parent_layout = self.current_schedule_table.parent().layout()
        index = parent_layout.indexOf(self.current_schedule_table)
        self.current_schedule_table.setParent(None)
        self.current_schedule_table = self.create_table(filtered_data, self.current_schedule_headers)
        parent_layout.insertWidget(index, self.current_schedule_table)

    # ==================== PATIENT PANEL ====================
    def show_patient_panel(self):
        self.save_current_panel()
        self.clear_right_panel()

        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(20, 20, 20, 20)

        header_layout = QHBoxLayout()
        
        title_label = QLabel("Patients")
        title_label.setFont(QFont("Futura Cyrillic Medium", 20, QFont.Bold))
        title_label.setStyleSheet("color: #373737;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        self.patient_search_input = QLineEdit()
        self.patient_search_input.setPlaceholderText("Search...")
        self.patient_search_input.setFixedSize(250, 35)
        self.patient_search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #f69623;
                border-radius: 5px;
                padding: 5px 10px;
                background-color: white;
            }
        """)
        self.patient_search_input.textChanged.connect(self.filter_patient_table)
        header_layout.addWidget(self.patient_search_input)

        main_layout.addLayout(header_layout)
        main_layout.addSpacing(15)

        self.all_patient_data = db.query("SELECT * FROM Customers")
        self.current_patient_headers = ["customer_id", "customer_name", "customer_cnum", "customer_email"]
        
        self.current_patient_table = self.create_table(self.all_patient_data, self.current_patient_headers)
        main_layout.addWidget(self.current_patient_table)

        self._right_layout.addWidget(self._back_button, alignment=Qt.AlignLeft)
        self._right_layout.addWidget(main_container)
        self.current_panel = main_container

    def filter_patient_table(self):
        search_text = self.patient_search_input.text().lower()
        filtered_data = self.all_patient_data if not search_text else [
            row for row in self.all_patient_data
            if any(search_text in str(value).lower() for value in row.values())
        ]
        
        parent_layout = self.current_patient_table.parent().layout()
        index = parent_layout.indexOf(self.current_patient_table)
        self.current_patient_table.setParent(None)
        self.current_patient_table = self.create_table(filtered_data, self.current_patient_headers)
        parent_layout.insertWidget(index, self.current_patient_table)

    # ==================== PRESCRIPTION PANEL ====================
    def show_prescription_panel(self):
        self.save_current_panel()
        self.clear_right_panel()

        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(20, 20, 20, 20)

        header_layout = QHBoxLayout()
        
        title_label = QLabel("Prescriptions")
        title_label.setFont(QFont("Futura Cyrillic Medium", 20, QFont.Bold))
        title_label.setStyleSheet("color: #373737;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        self.prescription_search_input = QLineEdit()
        self.prescription_search_input.setPlaceholderText("Search...")
        self.prescription_search_input.setFixedSize(250, 35)
        self.prescription_search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #f69623;
                border-radius: 5px;
                padding: 5px 10px;
                background-color: white;
            }
        """)
        self.prescription_search_input.textChanged.connect(self.filter_prescription_table)
        header_layout.addWidget(self.prescription_search_input)

        main_layout.addLayout(header_layout)
        main_layout.addSpacing(15)

        self.all_prescription_data = db.query("""
            SELECT p.prescription_id, c.customer_name, p.prescription_notes
            FROM Prescriptions p
            JOIN Customers c ON p.customer_id = c.customer_id
        """)
        self.current_prescription_headers = ["prescription_id", "customer_name", "prescription_notes"]
        
        self.current_prescription_table = self.create_table(self.all_prescription_data, self.current_prescription_headers)
        self.current_prescription_table.itemSelectionChanged.connect(self.on_prescription_row_selected)
        main_layout.addWidget(self.current_prescription_table)

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)

        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 10, 0, 0)

        form_grid = QGridLayout()
        form_grid.setHorizontalSpacing(15)
        form_grid.setVerticalSpacing(10)

        fields = ["prescription_id", "customer_id", "prescription_notes"]
        self.prescription_inputs = {}
        self.prescription_error_labels = {}

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
            
            if field == "prescription_id":
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
            
            self.prescription_inputs[field] = line_edit
            self.prescription_error_labels[field] = error_label

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

        add_btn.clicked.connect(self.add_prescription_db)
        update_btn.clicked.connect(self.update_prescription_db)
        delete_btn.clicked.connect(self.delete_prescription_db)

        button_layout.addWidget(add_btn)
        button_layout.addWidget(update_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addStretch()

        bottom_layout.addWidget(button_container, 1)
        main_layout.addLayout(bottom_layout)

        self._right_layout.addWidget(self._back_button, alignment=Qt.AlignLeft)
        self._right_layout.addWidget(main_container)
        self.current_panel = main_container

    def on_prescription_row_selected(self):
        if self.current_prescription_table.currentRow() >= 0:
            selected_row = self.current_prescription_table.currentRow()
            # Get prescription_id and prescription_notes from table
            prescription_id = self.current_prescription_table.item(selected_row, 0).text()
            prescription_notes = self.current_prescription_table.item(selected_row, 2).text()
            
            # Fetch customer_id from database using prescription_id
            result = db.query("SELECT customer_id FROM Prescriptions WHERE prescription_id=%s", (prescription_id,))
            customer_id = result[0]['customer_id'] if result else ""
            
            self.prescription_inputs["prescription_id"].setText(prescription_id)
            self.prescription_inputs["customer_id"].setText(str(customer_id))
            self.prescription_inputs["prescription_notes"].setText(prescription_notes)
            
            # Clear any error states
            for field in self.prescription_error_labels:
                self.clear_field_error(self.prescription_inputs[field], self.prescription_error_labels[field])

    def filter_prescription_table(self):
        search_text = self.prescription_search_input.text().lower()
        filtered_data = self.all_prescription_data if not search_text else [
            row for row in self.all_prescription_data
            if any(search_text in str(value).lower() for value in row.values())
        ]
        
        parent_layout = self.current_prescription_table.parent().layout()
        index = parent_layout.indexOf(self.current_prescription_table)
        self.current_prescription_table.setParent(None)
        self.current_prescription_table = self.create_table(filtered_data, self.current_prescription_headers)
        self.current_prescription_table.itemSelectionChanged.connect(self.on_prescription_row_selected)
        parent_layout.insertWidget(index, self.current_prescription_table)

    def refresh_prescription_table(self):
        self.all_prescription_data = db.query("""
            SELECT p.prescription_id, c.customer_name, p.prescription_notes
            FROM Prescriptions p
            JOIN Customers c ON p.customer_id = c.customer_id
        """)
        self.prescription_search_input.clear()
        parent_layout = self.current_prescription_table.parent().layout()
        index = parent_layout.indexOf(self.current_prescription_table)
        self.current_prescription_table.setParent(None)
        self.current_prescription_table = self.create_table(self.all_prescription_data, self.current_prescription_headers)
        self.current_prescription_table.itemSelectionChanged.connect(self.on_prescription_row_selected)
        parent_layout.insertWidget(index, self.current_prescription_table)

    def clear_prescription_form(self):
        for field in self.prescription_inputs:
            self.prescription_inputs[field].clear()
            if field in self.prescription_error_labels:
                self.clear_field_error(self.prescription_inputs[field], self.prescription_error_labels[field])

    def add_prescription_db(self):
        # Clear all previous errors
        for field in self.prescription_error_labels:
            self.clear_field_error(self.prescription_inputs[field], self.prescription_error_labels[field])
        
        fields = ["customer_id", "prescription_notes"]
        values = [self.prescription_inputs[f].text() for f in fields]
        
        if not all(values):
            QMessageBox.warning(self, "Warning", "Please fill all fields.")
            return
        
        # Validate each field
        has_error = False
        
        # Validate customer_id exists
        valid, error_msg = self.validate_customer_id_exists(values[0])
        if not valid:
            self.set_field_error(self.prescription_inputs["customer_id"], 
                               self.prescription_error_labels["customer_id"], error_msg)
            has_error = True
        
        # Validate prescription notes
        valid, error_msg = self.validate_prescription_notes(values[1])
        if not valid:
            self.set_field_error(self.prescription_inputs["prescription_notes"], 
                               self.prescription_error_labels["prescription_notes"], error_msg)
            has_error = True
        
        if has_error:
            QMessageBox.warning(self, "Validation Error", "Please fix the errors highlighted in red.")
            return
        
        db.execute("INSERT INTO Prescriptions (customer_id, prescription_notes) VALUES (%s,%s)", values)
        QMessageBox.information(self, "Success", "Prescription added successfully.")
        self.refresh_prescription_table()
        self.clear_prescription_form()

    def update_prescription_db(self):
        prescription_id = self.prescription_inputs["prescription_id"].text()
        if not prescription_id:
            QMessageBox.warning(self, "Warning", "Please select a prescription to update.")
            return
        
        # Clear all previous errors
        for field in self.prescription_error_labels:
            self.clear_field_error(self.prescription_inputs[field], self.prescription_error_labels[field])
        
        fields = ["customer_id", "prescription_notes"]
        values = [self.prescription_inputs[f].text() for f in fields]
        
        if not all(values):
            QMessageBox.warning(self, "Warning", "Please fill all fields.")
            return
        
        # Validate each field
        has_error = False
        
        # Validate customer_id exists
        valid, error_msg = self.validate_customer_id_exists(values[0])
        if not valid:
            self.set_field_error(self.prescription_inputs["customer_id"], 
                               self.prescription_error_labels["customer_id"], error_msg)
            has_error = True
        
        # Validate prescription notes
        valid, error_msg = self.validate_prescription_notes(values[1])
        if not valid:
            self.set_field_error(self.prescription_inputs["prescription_notes"], 
                               self.prescription_error_labels["prescription_notes"], error_msg)
            has_error = True
        
        if has_error:
            QMessageBox.warning(self, "Validation Error", "Please fix the errors highlighted in red.")
            return
        
        db.execute("UPDATE Prescriptions SET customer_id=%s, prescription_notes=%s WHERE prescription_id=%s",
                   (*values, prescription_id))
        QMessageBox.information(self, "Success", "Prescription updated successfully.")
        self.refresh_prescription_table()
        self.clear_prescription_form()

    def delete_prescription_db(self):
        prescription_id = self.prescription_inputs["prescription_id"].text()
        if not prescription_id:
            QMessageBox.warning(self, "Warning", "Please select a prescription to delete.")
            return
        reply = QMessageBox.question(self, "Confirm Delete", 
                                      f"Are you sure you want to delete prescription ID {prescription_id}?",
                                      QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            db.execute("DELETE FROM Prescriptions WHERE prescription_id=%s", (prescription_id,))
            QMessageBox.information(self, "Success", "Prescription deleted successfully.")
            self.refresh_prescription_table()
            self.clear_prescription_form()

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
    window = OptometristWindow()
    window.show()
    sys.exit(app.exec_())