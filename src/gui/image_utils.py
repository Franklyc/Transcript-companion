from PyQt6.QtWidgets import QLabel, QFileDialog, QMessageBox
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import os
import textract
from PIL import Image
from src.gui.lang import STRINGS
from src.gui.screenshot_dialog import ScreenshotDialog

def display_image(image_display, image_path):
    """在指定的QLabel上显示图像"""
    pixmap = QPixmap(image_path)
    if not pixmap.isNull():
        # Scale while maintaining aspect ratio
        pixmap = pixmap.scaled(
            image_display.width(), 
            image_display.maximumHeight(),
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        image_display.setPixmap(pixmap)
        return True
    return False

def process_ocr(parent, image_path):
    """处理OCR，从图像中提取文本"""
    try:
        text = textract.process(image_path).decode('utf-8')
        parent.ocr_text_edit.setText(text)
        parent.current_image_path = image_path
        display_image(parent.image_display, image_path)
        parent.status_label.setText(STRINGS[parent.parent.current_lang]['ocr_success'])
        parent.status_label.setStyleSheet("color: green")
        return True
    except Exception as e:
        parent.status_label.setText(f"{STRINGS[parent.parent.current_lang]['ocr_error']}: {e}")
        parent.status_label.setStyleSheet("color: red")
        return False

def process_screenshot(parent, image_path):
    """处理截图，显示图像"""
    parent.current_image_path = image_path
    display_image(parent.image_display, image_path)
    parent.status_label.setText(STRINGS[parent.parent.current_lang]['screenshot_success'])
    parent.status_label.setStyleSheet("color: green")

def upload_image(parent):
    """处理图像上传功能"""
    file_path, _ = QFileDialog.getOpenFileName(
        parent, 
        "Select Image", 
        "", 
        "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
    )
    
    if file_path:
        try:
            parent.current_image_path = file_path
            display_image(parent.image_display, file_path)
            parent.status_label.setText(STRINGS[parent.parent.current_lang]['image_upload_success'])
            parent.status_label.setStyleSheet("color: green")
            return True
        except Exception as e:
            parent.status_label.setText(f"{STRINGS[parent.parent.current_lang]['image_upload_error']}{e}")
            parent.status_label.setStyleSheet("color: red")
            return False
    return False

def clear_image(parent):
    """清除显示的图像"""
    parent.image_display.clear()
    parent.current_image_path = None
    parent.status_label.clear()

def start_screenshot_dialog(parent, mode):
    """启动截图对话框"""
    dialog = ScreenshotDialog(parent, mode)
    result = dialog.exec()
    
    # 获取主窗口并恢复显示
    main_window = parent.parent
    main_window.showNormal()
    main_window.activateWindow()
    main_window.raise_()
    
    if result == QFileDialog.DialogCode.Accepted:
        image_path = dialog.image_path
        if mode == "ocr":
            process_ocr(parent, image_path)
        else:
            process_screenshot(parent, image_path)
        return True
    else:
        mode_text = 'ocr_selection_canceled' if mode == 'ocr' else 'screenshot_canceled'
        parent.status_label.setText(STRINGS[parent.parent.current_lang][mode_text])
        parent.status_label.setStyleSheet("color: orange")
        return False