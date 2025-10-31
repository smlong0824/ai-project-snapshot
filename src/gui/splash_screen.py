"""Splash screen for Nova startup"""
from PyQt6.QtWidgets import QSplashScreen, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont

class NovaSplashScreen(QSplashScreen):
    def __init__(self):
        # Create a pixmap for splash
        pixmap = QPixmap(400, 300)
        pixmap.fill(QColor("#1e1e2e"))
        
        super().__init__(pixmap)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        
        # Draw content
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Nova logo text
        painter.setPen(QColor("#89b4fa"))
        font = QFont("Segoe UI", 48, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "NOVA")
        
        # Subtitle
        painter.setPen(QColor("#a6adc8"))
        font = QFont("Segoe UI", 12)
        painter.setFont(font)
        painter.drawText(pixmap.rect().adjusted(0, 80, 0, 0), 
                        Qt.AlignmentFlag.AlignCenter, "AI Dashboard")
        
        painter.end()
        self.setPixmap(pixmap)
    
    def showMessage(self, message: str):
        super().showMessage(
            message,
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
            QColor("#89b4fa")
        )
