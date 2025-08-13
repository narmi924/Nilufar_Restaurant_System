#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美莲花美食支出记录系统 - 登录窗口
使用 PyQt-Fluent-Widgets 实现现代化的 Fluent Design 界面
"""

import sys
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from qfluentwidgets import (TitleLabel, SubtitleLabel, BodyLabel, LineEdit, PasswordLineEdit, 
                            PrimaryPushButton, InfoBar, InfoBarIcon, InfoBarPosition,
                            setTheme, Theme)
from qfluentwidgets.components.widgets.frameless_window import FramelessWindow
from qframelesswindow import TitleBar
from models import verify_user, save_last_username, get_last_username


class LoginWindow(FramelessWindow):
    """
    登录窗口类 - 使用 Fluent Design 风格
    提供用户身份验证界面，采用现代化设计
    """
    # 定义自定义信号，当登录成功时会发出用户角色
    login_successful = pyqtSignal(str)
    
    def __init__(self, sound_manager=None):
        """
        初始化登录窗口
        
        Args:
            sound_manager: 声音管理器实例
        """
        super().__init__()
        self.sound_manager = sound_manager
        
        # --- 开始应用无边框和亚克力效果 ---
        # 1. 设置自定义标题栏，这将自动启用无边框模式并接管窗口操作
        self.setTitleBar(TitleBar(self))
        self.titleBar.raise_() # 将标题栏置于顶层

        # 2. 对窗口背景应用亚克力效果
        self.windowEffect.setAcrylicEffect(self.winId(), "F2F2F230") # A0是透明度

        # 3. 基础TitleBar没有titleLabel属性，无需隐藏

        # 4. 可选：固定窗口大小，因为登录窗口通常不需要缩放
        self.setFixedSize(550, 450)
        # --- 效果应用结束 ---
        
        self.init_ui()
    
    def init_ui(self):
        """
        初始化用户界面
        """
        # 设置窗口标题
        self.setWindowTitle("美莲花美食 - 登录 / نىلۇپەر تائاملار سارىيى - كىرىش")
        
        # 窗口大小已在__init__中设置为550x450，这里不再重复设置
        
        # 应用 Fluent Design 样式 - 移除自定义配色，使用主题色
        # Fluent Design 会自动应用正确的颜色方案，无需手动设置
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(50, 40, 50, 40)
        
        # 创建各个区域
        self.create_header_area(main_layout)
        self.create_input_area(main_layout)
        self.create_button_area(main_layout)
        
        # 添加弹性空间
        main_layout.addStretch()
        
        # 如果已有用户名，焦点设在密码框，否则设在用户名框
        if get_last_username():
            self.password_input.setFocus()
        else:
            self.username_input.setFocus()
    
    def create_header_area(self, parent_layout):
        """
        创建标题区域 - 使用 TitleLabel
        """
        # 系统标题 - 使用 Fluent Design 的 TitleLabel
        title_label = TitleLabel("美莲花美食支出记录系统")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 副标题 - 维语标题，使用 SubtitleLabel
        from qfluentwidgets import SubtitleLabel
        subtitle_label = SubtitleLabel("نىلۇپەر تائاملار سارىيى چىقىم خاتىرىسى")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        parent_layout.addWidget(title_label)
        parent_layout.addWidget(subtitle_label)
    
    def create_input_area(self, parent_layout):
        """
        创建输入区域 - 使用 Fluent Design 控件
        """
        # 创建输入容器
        input_frame = QWidget()
        input_layout = QVBoxLayout(input_frame)
        input_layout.setSpacing(25)
        input_layout.setContentsMargins(20, 20, 20, 20)
        
        # 用户名输入行
        username_row = QHBoxLayout()
        username_row.setSpacing(15)
        
        # 用户名标签 - 使用 Fluent Design 标签
        from qfluentwidgets import BodyLabel
        username_label = BodyLabel("用户名 / ئىشلەتكۈچى نامى")
        username_label.setMinimumWidth(120)
        username_label.setMaximumWidth(120)
        username_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        # 用户名输入框 - 使用 LineEdit
        self.username_input = LineEdit()
        self.username_input.setPlaceholderText("请输入用户名 / ئىشلەتكۈچى نامىنى كىرگۈزۈڭ")
        self.username_input.setMinimumHeight(40)
        
        # 设置默认用户名为最后使用的用户名
        last_username = get_last_username()
        if last_username:
            self.username_input.setText(last_username)
        
        username_row.addWidget(username_label)
        username_row.addWidget(self.username_input)
        
        # 密码输入行
        password_row = QHBoxLayout()
        password_row.setSpacing(15)
        
        # 密码标签 - 使用 Fluent Design 标签
        password_label = BodyLabel("密码 / مەخپىي نومۇر")
        password_label.setMinimumWidth(120)
        password_label.setMaximumWidth(120)
        password_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        # 密码输入框 - 使用专门的 PasswordLineEdit
        self.password_input = PasswordLineEdit()
        self.password_input.setPlaceholderText("请输入密码 / مەخپىي نومۇرنى كىرگۈزۈڭ")
        self.password_input.setMinimumHeight(40)
        
        password_row.addWidget(password_label)
        password_row.addWidget(self.password_input)
        
        # 添加到输入布局
        input_layout.addLayout(username_row)
        input_layout.addLayout(password_row)
        
        parent_layout.addWidget(input_frame)
    
    def create_button_area(self, parent_layout):
        """
        创建按钮区域 - 使用 PrimaryPushButton
        """
        # 创建按钮容器
        button_frame = QWidget()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 20, 0, 0)
        
        # 登录按钮 - 使用主题色的 PrimaryPushButton
        self.login_button = PrimaryPushButton("登录 / كىرىش")
        self.login_button.setMinimumHeight(45)
        self.login_button.setMinimumWidth(200)
        
        # 连接信号与槽
        self.login_button.clicked.connect(self.handle_login)
        
        # 连接音效
        if self.sound_manager:
            self.login_button.clicked.connect(self.sound_manager.play_confirmation)
        
        # 允许按回车键登录
        self.password_input.returnPressed.connect(self.handle_login)
        self.username_input.returnPressed.connect(self.handle_login)
        
        # 居中布局
        button_layout.addStretch()
        button_layout.addWidget(self.login_button)
        button_layout.addStretch()
        
        parent_layout.addWidget(button_frame)
    
    def handle_login(self):
        """
        处理登录逻辑 - 使用优雅的 InfoBar 替代 QMessageBox
        """
        # 获取用户输入的用户名和密码
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        # 检查输入是否为空
        if not username:
            InfoBar.warning(
                title='输入提醒',
                content="请输入用户名！/ ئىشلەتكۈچى نامىنى كىرگۈزۈڭ!",
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
            self.username_input.setFocus()
            return
        
        if not password:
            InfoBar.warning(
                title='输入提醒',
                content="请输入密码！/ مەخپىي نومۇرنى كىرگۈزۈڭ!",
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
            self.password_input.setFocus()
            return
        
        # 验证用户名和密码
        try:
            user_role = verify_user(username, password)
            
            if user_role is not None:
                # 登录成功提示
                InfoBar.success(
                    title='登录成功',
                    content="欢迎使用美莲花美食系统！/ نىلۇپەر تائاملار سارىيى سىستېمىسىغا مەرھابا!",
                    duration=2000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                
                # 保存最后使用的用户名
                save_last_username(username)
                # 发出登录成功的信号，传递用户角色
                self.login_successful.emit(user_role)
                # 关闭登录窗口
                self.close()
            else:
                # 登录失败 - 使用优雅的错误提示
                InfoBar.error(
                    title='登录失败',
                    content="用户名或密码错误，请重试！/ ئىشلەتكۈچى نامى ياكى مەخپىي نومۇر خاتا!",
                    duration=4000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                # 清空密码输入框并设置焦点
                self.password_input.clear()
                self.password_input.setFocus()
                
        except Exception as e:
            # 处理可能的数据库连接错误等异常
            InfoBar.error(
                title='系统错误',
                content=f"登录过程中发生错误：{str(e)} / سىستېما خاتالىقى كۆرۈلدى",
                duration=5000,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def keyPressEvent(self, event):
        """
        处理键盘事件
        """
        # 按ESC键关闭窗口
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)



