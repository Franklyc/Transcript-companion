from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout, QWidget
from PyQt6.QtGui import QPainter, QColor, QGuiApplication
from PyQt6.QtCore import Qt, QRect, QTimer
import os
import datetime
from src.gui.lang import STRINGS

class ScreenshotDialog(QDialog):
    def __init__(self, parent=None, mode="screenshot"):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(QGuiApplication.primaryScreen().geometry())
        self.setCursor(Qt.CursorShape.CrossCursor)
        
        self.mode = mode
        self.start_point = None
        self.end_point = None
        self.selection_rect = QRect()
        self.is_selecting = False
        self.image_path = None
        
        self.setMouseTracking(True)
        
        # Add an instruction label
        self.instruction = QLabel(STRINGS[parent.parent.current_lang]['screenshot_instructions' if mode == 'screenshot' else 'ocr_instructions'])
        self.instruction.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 150); padding: 10px; border-radius: 5px;")
        self.instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.instruction, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch()

    def paintEvent(self, event):
        painter = QPainter(self)
        
        # Draw semi-transparent overlay
        painter.fillRect(self.rect(), QColor(0, 0, 0, 30))
        
        # Draw selection rectangle if we're selecting
        if self.is_selecting and not self.selection_rect.isEmpty():
            # Draw the selection rectangle with a border
            painter.setPen(QColor(0, 162, 232, 255))  # Blue border
            painter.setBrush(QColor(0, 162, 232, 30))  # Semi-transparent blue fill
            painter.drawRect(self.selection_rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.position().toPoint()
            self.is_selecting = True
            self.selection_rect = QRect()
            self.update()

    def mouseMoveEvent(self, event):
        if self.is_selecting and self.start_point:
            self.end_point = event.position().toPoint()
            self.selection_rect = QRect(self.start_point, self.end_point).normalized()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_selecting:
            self.end_point = event.position().toPoint()
            self.selection_rect = QRect(self.start_point, self.end_point).normalized()
            self.is_selecting = False
            
            if self.selection_rect.width() > 10 and self.selection_rect.height() > 10:
                # Take the screenshot with a small delay to allow dialog to hide
                QTimer.singleShot(200, self.take_screenshot)
            else:
                self.reject()  # Cancel if the selection is too small

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        super().keyPressEvent(event)

    def take_screenshot(self):
        if not self.selection_rect.isValid() or self.selection_rect.isEmpty():
            self.reject()
            return
            
        screen = QGuiApplication.primaryScreen()
        screenshot = screen.grabWindow(0, self.selection_rect.x(), self.selection_rect.y(), 
                                      self.selection_rect.width(), self.selection_rect.height())
        
        # Create temp directory if needed
        temp_dir = os.path.join(os.getcwd(), "temp")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            
        # Save the screenshot
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        image_path = os.path.join(temp_dir, f"screenshot_{timestamp}.png")
        screenshot.save(image_path)
        
        # Pass the image path back through accept()
        self.image_path = image_path
        self.accept()

class SelectionOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QColor(100, 100, 100, 150))
        painter.setBrush(QColor(100, 100, 100, 50))
        rect = self.rect()
        painter.drawRect(rect)