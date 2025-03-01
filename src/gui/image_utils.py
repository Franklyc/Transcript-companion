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

def get_status_component(parent):
    """根据组件类型获取正确的状态标签组件"""
    # 尝试获取 parent 所属的主窗口
    if hasattr(parent, 'parent') and hasattr(parent.parent, 'content_area'):
        return parent.parent.content_area.output_area
    # 如果 parent 是 ContentArea
    elif hasattr(parent, 'output_area'):
        return parent.output_area
    # 如果都不是，返回 None
    return None

def process_ocr(parent, image_path):
    """处理OCR，从图像中提取文本"""
    try:
        text = textract.process(image_path).decode('utf-8')
        parent.ocr_text_edit.setText(text)
        parent.current_image_path = image_path
        display_image(parent.image_display, image_path)
        
        # 获取状态组件
        status_component = get_status_component(parent)
        if status_component:
            status_component.set_status(STRINGS[parent.parent.current_lang]['ocr_success'])
        return True
    except Exception as e:
        # 获取状态组件
        status_component = get_status_component(parent)
        if status_component:
            status_component.set_status(f"{STRINGS[parent.parent.current_lang]['ocr_error']}: {e}", True)
        return False

def process_screenshot(parent, image_path):
    """处理截图，显示图像"""
    parent.current_image_path = image_path
    display_image(parent.image_display, image_path)
    
    # 获取状态组件
    status_component = get_status_component(parent)
    if status_component:
        status_component.set_status(STRINGS[parent.parent.current_lang]['screenshot_success'])

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
            
            # 获取状态组件
            status_component = get_status_component(parent)
            if status_component:
                status_component.set_status(STRINGS[parent.parent.current_lang]['image_upload_success'])
            return True
        except Exception as e:
            # 获取状态组件
            status_component = get_status_component(parent)
            if status_component:
                status_component.set_status(f"{STRINGS[parent.parent.current_lang]['image_upload_error']}{e}", True)
            return False
    return False

def clear_image(parent):
    """清除显示的图像"""
    parent.image_display.clear()
    parent.current_image_path = None
    
    # 获取状态组件
    status_component = get_status_component(parent)
    if status_component:
        status_component.set_status("")

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
        
        # 获取状态组件
        status_component = get_status_component(parent)
        if status_component:
            status_component.set_status(STRINGS[parent.parent.current_lang][mode_text], True)
        return False