from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import os

class MagicGUI(QWidget):
    
    #load the css file for the page requested
    def load_css(self, filename):
        file = QFile(filename)
        if not file.open(QFile.ReadOnly | QFile.Text):
            print(f"Unable to open the stylesheet file: {filename}")
            return ""
        
        stream = QTextStream(file)
        return stream.readAll()

    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("MTG GUI")
        self.setGeometry(100, 100, 800, 700)
        self.draw_homepage()

    #All Homepage Functions ----------------
    def draw_homepage(self):
        main_window = QVBoxLayout()

        #Title Text
        title = QLabel('Magic the Gathering Personal Database')
        title.setAlignment(Qt.AlignBottom)
        title.setObjectName("title")
        main_window.addWidget(title)

        #middle buttons
        button_window = QHBoxLayout()

        # BUTTON WINDOW BUTTONS ----
        scanner_button = QPushButton("Scanner")
        scanner_button.setObjectName("homepage_buttons")
        scanner_button.clicked.connect(self.draw_scannerpage)
        button_window.addWidget(scanner_button)

        deck_button = QPushButton("Deck Finder")
        deck_button.setObjectName("homepage_buttons")
        deck_button.clicked.connect(self.draw_deckpage)
        button_window.addWidget(deck_button)
        # --------------------------
        button_window.setAlignment(Qt.AlignTop)
        main_window.addLayout(button_window)

        about_button = QPushButton("About")
        about_button.setObjectName("about_button")
        about_button.clicked.connect(self.about_popup)
        main_window.addWidget(about_button, alignment=Qt.AlignRight)

        #setting cursors
        scanner_button.setCursor(Qt.PointingHandCursor) 
        deck_button.setCursor(Qt.PointingHandCursor)


        self.setLayout(main_window)

        #Load Homepage CSS
        stylesheet = self.load_css(f"{os.path.dirname(__file__)}/css/home.css")
        app.setStyleSheet(stylesheet)


    def about_popup(self):
        PopupWindow.show_popup(self)

    def draw_scannerpage(self):
        scanner_window = QHBoxLayout()
    def draw_deckpage(self):
        deck_window = QHBoxLayout()

#mini class for the About Popup Window
class PopupWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("About the Program")
        self.setGeometry(400, 400, 300, 200)

        layout = QVBoxLayout()
        label = QLabel("This is a personal project to learn python and understand some of its many libraries!", self)
        label.setWordWrap(True)
        layout.addWidget(label)

        label2 = QLabel("Property of Spencer Bone", self)
        layout.addWidget(label2)

        close_button = QPushButton("Close", self)
        close_button.setFixedWidth(50)
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button, alignment=Qt.AlignRight)

        self.setLayout(layout)
    def show_popup(self):
        # Show the custom popup window
        self.popup = PopupWindow()
        self.popup.show()

app = QApplication(sys.argv)
window = MagicGUI()
window.show()
sys.exit(app.exec_())