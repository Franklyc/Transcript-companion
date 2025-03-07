from PyQt6.QtWidgets import QLabel, QFileDialog, QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtGui import QPixmap, QGuiApplication
from PyQt6.QtCore import Qt
import os
import textract
from PIL import Image
import datetime
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
        
        # 添加新图像到列表
        add_image_to_collection(parent, image_path)
        
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
    # 添加新图像到列表
    add_image_to_collection(parent, image_path)
    
    # 获取状态组件
    status_component = get_status_component(parent)
    if status_component:
        status_component.set_status(STRINGS[parent.parent.current_lang]['screenshot_success'])

def add_image_to_collection(parent, image_path):
    """将图像添加到图像集合中"""
    # 确保有图像集合列表
    if not hasattr(parent, 'image_paths'):
        parent.image_paths = []
    
    # 添加新图像到列表
    if image_path not in parent.image_paths:
        parent.image_paths.append(image_path)
    
    # 更新图像预览区
    update_image_previews(parent)

def upload_image(parent):
    """处理图像上传功能"""
    files, _ = QFileDialog.getOpenFileNames(
        parent, 
        "Select Images", 
        "", 
        "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
    )
    
    if files:
        try:
            for file_path in files:
                # 添加每一个图像
                add_image_to_collection(parent, file_path)
            
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

def clear_image(parent, image_path=None):
    """清除指定的图像或所有图像"""
    if image_path is None:
        # 清除所有图像
        if hasattr(parent, 'image_paths'):
            parent.image_paths = []
        if hasattr(parent, 'images_container') and parent.images_container is not None:
            # 清除图像容器中的所有小部件
            layout = parent.images_container.layout()
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
    else:
        # 清除指定图像
        if hasattr(parent, 'image_paths') and image_path in parent.image_paths:
            parent.image_paths.remove(image_path)
    
    # 更新图像预览区
    update_image_previews(parent)
    
    # 获取状态组件
    status_component = get_status_component(parent)
    if status_component:
        status_component.set_status("")

def remove_image(parent, image_path):
    """从集合中移除指定的图像"""
    clear_image(parent, image_path)

def update_image_previews(parent):
    """更新图像预览区域，显示所有已添加的图像"""
    if not hasattr(parent, 'images_container') or parent.images_container is None:
        return

    # 清除现有的图像预览
    layout = parent.images_container.layout()
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
    
    # 没有图像时显示提示
    if not hasattr(parent, 'image_paths') or not parent.image_paths:
        empty_label = QLabel(STRINGS[parent.parent.current_lang]['image_preview'])
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(empty_label)
        return
    
    # 添加每一个图像的预览
    for idx, img_path in enumerate(parent.image_paths):
        image_widget = QWidget()
        image_layout = QVBoxLayout(image_widget)
        image_layout.setContentsMargins(0, 0, 0, 0)
        image_layout.setSpacing(2)
        
        # 图像标签
        image_label = QLabel()
        image_label.setObjectName(f"imageDisplay_{idx}")
        image_label.setMinimumSize(150, 80)
        image_label.setMaximumHeight(100)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        display_image(image_label, img_path)
        
        # 图像控制按钮
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        
        # 移除按钮
        remove_btn = QPushButton(STRINGS[parent.parent.current_lang]['remove_image'])
        remove_btn.setObjectName(f"removeBtn_{idx}")
        remove_btn.setFixedHeight(20)
        remove_btn.clicked.connect(lambda checked, path=img_path: remove_image(parent, path))
        btn_layout.addWidget(remove_btn)
        
        # 添加到布局
        image_layout.addWidget(image_label)
        image_layout.addLayout(btn_layout)
        
        layout.addWidget(image_widget)

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

def take_fullscreen_screenshot(parent, mode="screenshot"):
    """截取整个屏幕"""
    try:
        # 获取主屏幕
        screen = QGuiApplication.primaryScreen()
        
        # 截取整个屏幕
        screenshot = screen.grabWindow(0)
        
        # 创建临时目录
        temp_dir = os.path.join(os.getcwd(), "temp")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        # 保存截图
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        image_path = os.path.join(temp_dir, f"fullscreen_{timestamp}.png")
        screenshot.save(image_path)
        
        # 根据模式处理图像
        if mode == "ocr":
            process_ocr(parent, image_path)
        else:
            process_screenshot(parent, image_path)
        
        return True
    except Exception as e:
        # 获取状态组件
        status_component = get_status_component(parent)
        if status_component:
            status_component.set_status(f"全屏截图失败: {e}", True)
        return False