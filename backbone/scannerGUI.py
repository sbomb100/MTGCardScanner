from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget, QPushButton
import sys
from scanner import CardScanner  # Import your scanner class

class ScannerGUI(QMainWindow):