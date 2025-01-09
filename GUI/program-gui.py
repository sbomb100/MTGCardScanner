from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import os
import cv2
from scanner import CardScanner
import numpy as np

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

    #Making the About Popup Window
    def about_popup(self):
        PopupWindow.show_popup(self)

    def delete_old_layout(self):
        #delete old layout
        QWidget().setLayout(self.layout())
        layout = QGridLayout(self)
        QObjectCleanupHandler().add(self.layout())
    

    #SCANNER METHODS
    def setup_scanner(self):
        # Initialize the scanner
        self.scanner = CardScanner()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.scanner_running = False
        self.last_card = ""

    def update_frame(self):
        """Capture a frame and update the GUI."""
        if not self.scanner_running:
            black_square = np.zeros((640, 480, 3), dtype=np.uint8)

            # Convert to QImage
            height, width, channel = black_square.shape
            bytes_per_line = channel * width
            q_image = QImage(black_square.data, width, height, bytes_per_line, QImage.Format_RGB888)

            # Update the QLabel
            self.video_label.setPixmap(QPixmap.fromImage(q_image))
        else:
            frame = self.scanner.read_frame()
            if frame is not None:
                # Convert the frame to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rotated = cv2.rotate(frame_rgb, cv2.ROTATE_90_CLOCKWISE)
                # Convert the frame to QImage
                height, width, channel = rotated.shape
                bytes_per_line = channel * width
                q_image = QImage(rotated.data, width, height, bytes_per_line, QImage.Format_RGB888)

                # Display the frame in the QLabel
                self.video_label.setPixmap(QPixmap.fromImage(q_image))

                # Analyze the frame for card information
                result = self.scanner.analyze_card(frame)
                
                if result != "" and result != self.last_card:
                    self.result_label.setText(result)
                    self.last_card = result
            else:
                self.toggle_scanner()

    def toggle_scanner(self):
        """Start or stop the scanner."""
        if self.scanner_running:
            self.timer.stop()
            self.scanner_running = False
            self.update_frame() #extra update to go back to black screen
            self.toggle_button.setText("Start Scanner")
            self.scanner.shutdown()

        else:
            self.timer.start(30)  # Update every 30ms
            self.scanner_running = True
            self.toggle_button.setText("Stop Scanner")


    def closeEvent(self, event):
        """Release resources on window close."""
        if self.scanner_running:
            self.scanner.shutdown()
        super().closeEvent(event)


    #Changing the layout to the scanner page
    def draw_scannerpage(self):
        self.setup_scanner()

        self.delete_old_layout()
        scanner_window = QHBoxLayout()
       
        #Camera Side Vertical Box ----
        camera_box = QVBoxLayout()
        self.video_label = QLabel("Camera Feed")
        black_square = np.zeros((640, 480, 3), dtype=np.uint8)
        # Convert to QImage
        height, width, channel = black_square.shape
        bytes_per_line = channel * width
        q_image = QImage(black_square.data, width, height, bytes_per_line, QImage.Format_RGB888)

        self.video_label.setPixmap(QPixmap.fromImage(q_image))
        self.video_label.setAlignment(Qt.AlignCenter)
        camera_box.addWidget(self.video_label)

        
        self.toggle_button = QPushButton("Start Scanner")
        self.toggle_button.clicked.connect(self.toggle_scanner)
        camera_box.addWidget(self.toggle_button)

        #Last Card Scanned Vertical Box
        last_scanned_box = QVBoxLayout()

        
        self.result_label = QLabel("Card Analysis Result")
        self.result_label.setAlignment(Qt.AlignCenter)
        last_scanned_box.addWidget(self.result_label)
        
        scanner_window.addLayout(camera_box)
        scanner_window.addLayout(last_scanned_box)
        self.setLayout(scanner_window)
    
    #Changing the layout to the deck page
    def draw_deckpage(self):
        self.delete_old_layout()
        deck_window = QHBoxLayout()

        #Left Side Vertical Box

        #Right Side Vertical Box

        self.setLayout(deck_window)

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