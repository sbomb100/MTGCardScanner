from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
import sys

class PopupWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Custom Popup")
        self.setGeometry(150, 150, 200, 150)

        layout = QVBoxLayout()
        label = QLabel("This is a custom popup window!", self)
        layout.addWidget(label)

        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Custom Popup Example")
        self.setGeometry(100, 100, 300, 200)

        # Create a button to show the popup
        button = QPushButton("Open Popup", self)
        button.clicked.connect(self.show_popup)
        button.resize(button.sizeHint())
        button.move(100, 70)

    def show_popup(self):
        # Show the custom popup window
        self.popup = PopupWindow()
        self.popup.show()

app = QApplication(sys.argv)
window = MyWindow()
window.show()
sys.exit(app.exec_())