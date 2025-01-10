from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtCore
import sys
import os
import cv2
from scanner import CardScanner
import numpy as np
import requests
from functools import partial

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

        #scanner initial state to save information
        self.scanner_running = False
        self.list_oldscans = "No Previous Scans"
        self.last_card_pixels = None


    
    def init_ui(self):
        self.setWindowTitle("MTG GUI")
        self.setGeometry(100, 100, 800, 700)
        self.setLayout(QHBoxLayout())
        self.draw_homepage()

    #All Homepage Functions ----------------
    def draw_homepage(self):
        self.clear_layout(self.layout())

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


        self.layout().addLayout(main_window)

        #Load Homepage CSS
        stylesheet = self.load_css(f"{os.path.dirname(__file__)}/css/home.css")
        app.setStyleSheet(stylesheet)

    #Making the About Popup Window
    def about_popup(self):
        InfoWindow.show_popup(self, "About", 
            """This program is designed to scan and store magic cards in a local databse. The point is to make it easier to figure out which cards I own""")

    def clear_layout(self, layout):
    # Iterate through all child widgets and layouts in the layout
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)  # Get the first item in the layout

                # If the item is a widget, delete it
                if item.widget():
                    widget = item.widget()
                    widget.deleteLater()  # Safely delete the widget
                # If the item is a layout, clear its child items
                elif item.layout():
                    self.clear_layout(item.layout())  # Recursively clear nested layouts
                    item.layout().deleteLater()  # Delete the sub-layout
    

    #SCANNER METHODS
    def setup_scanner(self):
        # Initialize the scanner
        self.scanner = CardScanner()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.scanner_running = False
        self.scanner_open = True
        self.last_card = ""

    def update_frame(self):
        #Capture a frame and update the GUI.
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
                    self.result_label.setText(result[1])
                    self.last_card = result

                    index = self.list_oldscans.find("\n")
                    if index != -1 and len(self.list_oldscans.splitlines()) >= 15:
                        self.list_oldscans = self.list_oldscans[index+1:] + result[1] + "\n"
                    elif index != -1:
                        self.list_oldscans = self.list_oldscans + result[1] + "\n"
                    else:
                        self.list_oldscans = result[1] + "\n"
                    
                    
                    response = requests.get(result[7])
                    if response.status_code == 200:
                        pixmap = QPixmap()
                        pixmap.loadFromData(response.content)
                        self.last_card_img.setPixmap(pixmap)
                        self.last_card_img.setAlignment(Qt.AlignCenter)
                        self.last_card_pixels = pixmap
            else:
                self.toggle_scanner()

    def toggle_scanner(self):
        #Start or stop the scanner.
        if self.scanner_running:
            self.timer.stop()
            self.scanner_running = False
            self.update_frame() #extra update to go back to black screen
            self.toggle_button.setText("Start Scanner")
            self.scanner.turn_off()
        else:
            self.toggle_button.setText("Starting Scanner...")
            self.scanner.turn_on()
            self.timer.start(20)  # Update every 30ms
            self.scanner_running = True
            self.toggle_button.setText("Stop Scanner")
            


    def closeEvent(self, event):
        #Release resources on window close.
        if self.scanner_running:
            self.scanner_open = False
            self.timer.stop()
            self.scanner.shutdown()
        super().closeEvent(event)
        
    def change_page(self, index):
        if self.scanner_open == True:
            self.scanner_open = False
            self.close_scanner()
            self.timer.stop()
        if index == -1:
            self.draw_homepage()
        elif index == 0:
            self.draw_scannerpage()
        elif index == 1:
            self.draw_deckpage()

    def draw_header(self, page_num):
        header_box = QHBoxLayout()
        # logo, dropdown box, search bar
        home_button = QPushButton("MTG-PC")
        #TODO: MAKE LOGO
        #pixmap = QPixmap("logo.png")  # Replace with your logo file
        #logo_label.setPixmap(pixmap)
        home_button.clicked.connect(partial(self.change_page, -1))
        header_box.addWidget(home_button)

        dropdown = QComboBox()
        dropdown.addItems(["Scanner", "Deck Finder"])
        dropdown.setCurrentIndex(page_num)
        dropdown.currentIndexChanged.connect(self.change_page)
        header_box.addWidget(dropdown)

        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search...")
        header_box.addWidget(search_bar)

        search_button = QPushButton("Search")
        #search_button.clicked.connect(self.perform_search)
        header_box.addWidget(search_button)

        return header_box

    def old_scans(self):
        InfoWindow.show_popup(self, "Previous Scans", self.list_oldscans)
            
    #Changing the layout to the scanner page
    def draw_scannerpage(self):
        self.setup_scanner()
        self.scanner_open = True
        self.clear_layout(self.layout())
        main_scanner_window = QVBoxLayout()
        
        main_scanner_window.addLayout(self.draw_header(0))
        scanner_window = QHBoxLayout()

        #Camera Side Vertical Box ----
        camera_box = QVBoxLayout()

        cam_text = QLabel()
        cam_text.setText("Camera Feed - Have Card Fill the Camera")
        camera_box.addWidget(cam_text)

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

        self.last_card_img = QLabel("Last Card Image")
        if self.last_card_pixels is not None:
            self.last_card_img.setPixmap(self.last_card_pixels)

        self.last_card_img.setAlignment(Qt.AlignCenter)
        last_scanned_box.addWidget(self.last_card_img)

        #"Card Analysis Result"
        self.result_label = QLabel()
        if self.list_oldscans.find("\n") != -1:
            self.result_label.setText(self.list_oldscans.splitlines()[-1])
        else:
            self.result_label.setText("Card Analysis Result")
        self.result_label.setAlignment(Qt.AlignCenter)
        last_scanned_box.addWidget(self.result_label)
        
        self.previous_scans = QPushButton("Old Scans Here")
        self.previous_scans.clicked.connect(self.old_scans)
        last_scanned_box.addWidget(self.previous_scans)

        scanner_window.addLayout(camera_box)
        scanner_window.addLayout(last_scanned_box)
        main_scanner_window.addLayout(scanner_window)

        self.layout().addLayout(main_scanner_window)
    
    def close_scanner(self):
        if self.scanner_running:
            self.scanner.turn_off()
        self.scanner_running = False


    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress and obj is self.file_box:
            if event.key() == QtCore.Qt.Key_Return and self.file_box.hasFocus():
                print(self.file_box.text())
                #TODO LINK TO DECK MAKER
        return super().eventFilter(obj, event)
    
    #Changing the layout to the deck page
    def draw_deckpage(self):
        self.scanner_open = False
        self.clear_layout(self.layout())

        deck_window = QVBoxLayout()

        deck_window.addLayout(self.draw_header(1))

        middle_screen = QHBoxLayout()
        #Left Side Vertical Box
            #paste box
        left_side = QVBoxLayout()
        paste_window = QVBoxLayout()
        paste_label = QLabel("Paste Deck List:")
        paste_window.addWidget(paste_label)
        self.paste_box =  QTextEdit()
        self.paste_box.setPlaceholderText("Paste your wanted deck here...")
        paste_window.addWidget(self.paste_box)
        paste_button = QPushButton("Process Card List")
        #self.process_button.clicked.connect(self.process_cards)
        paste_window.addWidget(paste_button)
        left_side.addLayout(paste_window)

        or_label = QLabel("------- OR -------")
        left_side.addWidget(or_label)

            #file name
        file_window = QVBoxLayout()
        file_label = QLabel("Text File Name Here:")
        file_window.addWidget(file_label)
        self.file_box =  QLineEdit()
        self.file_box.setPlaceholderText("Text File Name Here:")
        self.file_box.installEventFilter(self)

        file_window.addWidget(self.file_box)
        left_side.addLayout(file_window)
        middle_screen.addLayout(left_side)

        #Right Side Vertical Box
        right_side = QVBoxLayout()
        self.output_box =  QTextEdit()
        self.output_box.setPlaceholderText("Deck Output Here...")
        right_side.addWidget(self.output_box)
        outputDL_button = QPushButton("Download Deck as Text File")
        #self.outputDL_button.clicked.connect(self.download_deck_output)
        right_side.addWidget(outputDL_button)
        middle_screen.addLayout(right_side)

        deck_window.addLayout(middle_screen)
        self.layout().addLayout(deck_window)

#mini class for the About Popup Window
class InfoWindow(QWidget):
    def __init__(self, header, text):
        super().__init__()

        self.setWindowTitle(header)
        self.setGeometry(400, 400, 300, 200)

        layout = QVBoxLayout()
        label = QLabel(text, self)
        label.setWordWrap(True)
        layout.addWidget(label)

        close_button = QPushButton("Close", self)
        close_button.setFixedWidth(50)
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button, alignment=Qt.AlignRight)

        self.setLayout(layout)

    def show_popup(self, header, text):
        self.popup = InfoWindow(header, text)
        self.popup.show()

app = QApplication(sys.argv)
window = MagicGUI()
window.show()
sys.exit(app.exec_())
