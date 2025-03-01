from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                           QPushButton, QComboBox, QGridLayout, QFileDialog)
from PyQt6.QtCore import pyqtSignal
import src.config.config
from src.gui.lang import STRINGS

class SettingsTab(QWidget):
    """设置选项卡，用于管理文件夹、模型选择等基本设置"""
    
    folder_selected = pyqtSignal(str)
    provider_changed = pyqtSignal(str)
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        
    def init_ui(self):
        """初始化设置选项卡UI"""
        settings_layout = QVBoxLayout(self)
        settings_layout.setContentsMargins(5, 5, 5, 5)
        settings_layout.setSpacing(5)
        
        # 创建网格布局
        grid_layout = QGridLayout()
        grid_layout.setVerticalSpacing(8)
        grid_layout.setHorizontalSpacing(8)
        
        # 文件夹选择
        self.folder_edit = QLineEdit(src.config.config.DEFAULT_FOLDER_PATH)
        self.folder_edit.setReadOnly(True)
        self.folder_button = QPushButton(STRINGS[self.parent.current_lang]['select_folder'])
        self.folder_button.setObjectName("folderButton")
        self.folder_button.setFixedHeight(28)
        self.folder_label = QLabel(STRINGS[self.parent.current_lang]['current_folder'])
        grid_layout.addWidget(self.folder_label, 0, 0)
        grid_layout.addWidget(self.folder_edit, 0, 1)
        grid_layout.addWidget(self.folder_button, 0, 2)
        
        # 提供商选择
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(src.config.config.PROVIDERS)
        self.provider_combo.setCurrentText(src.config.config.DEFAULT_PROVIDER)
        self.provider_combo.setFixedHeight(28)
        self.provider_label = QLabel(STRINGS[self.parent.current_lang].get('select_provider', 'Select Provider:'))
        grid_layout.addWidget(self.provider_label, 1, 0)
        grid_layout.addWidget(self.provider_combo, 1, 1, 1, 2)
        
        # 模型选择
        self.model_combo = QComboBox()
        self.model_combo.setFixedHeight(28)
        self.update_model_list(include_local=False)
        self.model_label = QLabel(STRINGS[self.parent.current_lang]['select_model'])
        grid_layout.addWidget(self.model_label, 2, 0)
        grid_layout.addWidget(self.model_combo, 2, 1, 1, 2)
        
        # 温度设置
        self.temp_edit = QLineEdit(src.config.config.DEFAULT_TEMPERATURE)
        self.temp_edit.setFixedHeight(28)
        self.temp_label = QLabel(STRINGS[self.parent.current_lang]['set_temperature'])
        grid_layout.addWidget(self.temp_label, 3, 0)
        grid_layout.addWidget(self.temp_edit, 3, 1, 1, 2)
        
        settings_layout.addLayout(grid_layout)
        
        # 连接信号
        self.folder_button.clicked.connect(self.select_folder)
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)
        
    def update_model_list(self, include_local=False):
        """更新模型列表"""
        current_model = self.model_combo.currentText() if self.model_combo.count() > 0 else ""
        src.config.config.refresh_available_models(include_local)
        self.model_combo.clear()

        # Filter models by selected provider
        provider = self.provider_combo.currentText()
        filtered_models = src.config.config.filter_models_by_provider(provider)
        self.model_combo.addItems(filtered_models)

        # Try to restore previous selection
        index = self.model_combo.findText(current_model)
        if (index >= 0):
            self.model_combo.setCurrentIndex(index)
        elif self.model_combo.count() > 0:
            self.model_combo.setCurrentIndex(0)
            
    def on_provider_changed(self, provider):
        """处理提供商选择变更"""
        self.update_model_list(self.provider_combo.currentText() in ["LMstudio", "Kobold", "Ollama"])
        self.provider_changed.emit(provider)
        
    def select_folder(self):
        """打开文件夹选择对话框"""
        folder_path = QFileDialog.getExistingDirectory(self)
        if folder_path:
            self.folder_edit.setText(folder_path)
            self.folder_selected.emit(folder_path)
            
    def get_selected_model(self):
        """获取当前选择的模型"""
        return self.model_combo.currentText()
        
    def get_temperature(self):
        """获取设置的温度值"""
        return self.temp_edit.text()
        
    def get_folder_path(self):
        """获取当前选择的文件夹路径"""
        return self.folder_edit.text()
    
    def update_texts(self):
        """更新界面上的文本为当前语言"""
        self.folder_label.setText(STRINGS[self.parent.current_lang]['current_folder'])
        self.folder_button.setText(STRINGS[self.parent.current_lang]['select_folder'])
        self.provider_label.setText(STRINGS[self.parent.current_lang]['select_provider'])
        self.model_label.setText(STRINGS[self.parent.current_lang]['select_model'])
        self.temp_label.setText(STRINGS[self.parent.current_lang]['set_temperature'])
    
    def apply_theme(self, theme):
        """应用主题样式"""
        font_family = src.config.config.UI_FONT_FAMILY
        font_size = src.config.config.UI_FONT_SIZE_NORMAL
        border_radius = src.config.config.UI_BORDER_RADIUS
        padding = src.config.config.UI_PADDING_SMALL
        
        self.setStyleSheet(f"""
            QWidget {{
                font-family: {font_family};
            }}
            QLabel {{
                font-size: {font_size};
                color: {theme['text']};
            }}
            QLineEdit, QComboBox {{
                font-size: {font_size};
                padding: {padding};
                border: 1px solid {theme['input_border']};
                border-radius: {border_radius};
                background-color: {theme['input_bg']};
                color: {theme['text']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {theme['dropdown_bg']};
                color: {theme['dropdown_text']};
                selection-background-color: {theme['button_bg']};
                selection-color: {theme['button_text']};
            }}
            QPushButton {{
                background-color: {theme['button_bg']};
                color: {theme['button_text']};
                padding: {padding};
                border-radius: {border_radius};
                font-size: {font_size};
            }}
            QPushButton:hover {{
                background-color: {theme['button_hover']};
            }}
            #folderButton {{
                min-width: 100px;
            }}
        """)