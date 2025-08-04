import sys
import qrcode
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QWidget, QLabel, QLineEdit, QPushButton, QComboBox,
                             QSpinBox, QColorDialog, QFileDialog, QMessageBox,
                             QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QColor
from PIL import Image
import os


class QRCodeGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.fill_color = "black"
        self.back_color = "white"
        self.qr_image = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("QR Code Generator")
        self.setGeometry(100, 100, 600, 700)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Input section
        input_group = QGroupBox("Input")
        input_layout = QVBoxLayout(input_group)

        self.url_label = QLabel("Enter URL or Text:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com or any text")

        input_layout.addWidget(self.url_label)
        input_layout.addWidget(self.url_input)

        # Settings section
        settings_group = QGroupBox("QR Code Settings")
        settings_layout = QGridLayout(settings_group)

        # Error correction level
        settings_layout.addWidget(QLabel("Error Correction:"), 0, 0)
        self.error_correction = QComboBox()
        self.error_correction.addItems(["Low (L)", "Medium (M)", "Quartile (Q)", "High (H)"])
        self.error_correction.setCurrentIndex(3)  # Default to High
        settings_layout.addWidget(self.error_correction, 0, 1)

        # Box size
        settings_layout.addWidget(QLabel("Box Size:"), 1, 0)
        self.box_size = QSpinBox()
        self.box_size.setRange(1, 50)
        self.box_size.setValue(10)
        settings_layout.addWidget(self.box_size, 1, 1)

        # Border
        settings_layout.addWidget(QLabel("Border:"), 2, 0)
        self.border = QSpinBox()
        self.border.setRange(0, 20)
        self.border.setValue(4)
        settings_layout.addWidget(self.border, 2, 1)

        # Color settings
        color_layout = QHBoxLayout()

        self.fill_color_btn = QPushButton("Fill Color")
        self.fill_color_btn.setStyleSheet(f"background-color: {self.fill_color}; color: white;")
        self.fill_color_btn.clicked.connect(self.choose_fill_color)

        self.back_color_btn = QPushButton("Background Color")
        self.back_color_btn.setStyleSheet(f"background-color: {self.back_color}; color: black;")
        self.back_color_btn.clicked.connect(self.choose_back_color)

        color_layout.addWidget(self.fill_color_btn)
        color_layout.addWidget(self.back_color_btn)

        settings_layout.addLayout(color_layout, 3, 0, 1, 2)

        # Generate button
        self.generate_btn = QPushButton("Generate QR Code")
        self.generate_btn.clicked.connect(self.generate_qr_code)
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        # Preview section
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)

        self.preview_label = QLabel("QR Code will appear here")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(300, 300)
        self.preview_label.setStyleSheet("border: 2px dashed #ccc; background-color: #f9f9f9;")

        preview_layout.addWidget(self.preview_label)

        # Save button
        self.save_btn = QPushButton("Save QR Code")
        self.save_btn.clicked.connect(self.save_qr_code)
        self.save_btn.setEnabled(False)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)

        # Add all sections to main layout
        main_layout.addWidget(input_group)
        main_layout.addWidget(settings_group)
        main_layout.addWidget(self.generate_btn)
        main_layout.addWidget(preview_group)
        main_layout.addWidget(self.save_btn)

    def choose_fill_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.fill_color = color.name()
            self.fill_color_btn.setStyleSheet(f"background-color: {self.fill_color}; color: white;")

    def choose_back_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.back_color = color.name()
            # Choose text color based on background brightness
            text_color = "black" if self.is_light_color(color) else "white"
            self.back_color_btn.setStyleSheet(f"background-color: {self.back_color}; color: {text_color};")

    def is_light_color(self, color):
        # Calculate relative luminance to determine if color is light
        r, g, b = color.red(), color.green(), color.blue()
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return luminance > 0.5

    def generate_qr_code(self):
        url = self.url_input.text().strip()

        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a URL or text!")
            return

        try:
            # Map error correction levels
            error_levels = {
                0: qrcode.constants.ERROR_CORRECT_L,
                1: qrcode.constants.ERROR_CORRECT_M,
                2: qrcode.constants.ERROR_CORRECT_Q,
                3: qrcode.constants.ERROR_CORRECT_H
            }

            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=error_levels[self.error_correction.currentIndex()],
                box_size=self.box_size.value(),
                border=self.border.value()
            )

            qr.add_data(url)
            qr.make(fit=True)

            # Generate image
            self.qr_image = qr.make_image(fill_color=self.fill_color, back_color=self.back_color)

            # Convert PIL image to QPixmap for display
            temp_path = "temp_qr.png"
            self.qr_image.save(temp_path)

            pixmap = QPixmap(temp_path)
            scaled_pixmap = pixmap.scaled(280, 280, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview_label.setPixmap(scaled_pixmap)

            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

            self.save_btn.setEnabled(True)
            QMessageBox.information(self, "Success", "QR Code generated successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate QR code: {str(e)}")

    def save_qr_code(self):
        if self.qr_image is None:
            QMessageBox.warning(self, "Warning", "Please generate a QR code first!")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save QR Code",
            "qrcode.png",
            "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)"
        )

        if file_path:
            try:
                self.qr_image.save(file_path)
                QMessageBox.information(self, "Success", f"QR Code saved as '{file_path}'!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save QR code: {str(e)}")


def main():
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle('Fusion')

    window = QRCodeGenerator()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()