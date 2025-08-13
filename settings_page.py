#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美莲花美食支出记录系统 - 设置页面
基于 Fluent Design 的功能页面，可嵌入到 NavigationInterface 中
"""

import sys
import os
import configparser
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QApplication, QMainWindow)
from qfluentwidgets import (TitleLabel, SubtitleLabel, BodyLabel, 
                            LineEdit, PasswordLineEdit, PrimaryPushButton, PushButton, 
                            ScrollArea, CardWidget, InfoBar, InfoBarPosition,
                            MessageBox, SegmentedWidget)

from models import (update_user_credentials, get_all_users, add_user, delete_user,
                    get_all_categories, add_category, delete_category, update_category)
from workers import ConnectionTestWorker


class SettingsPage(QWidget):
    """
    设置页面类 - 使用 Fluent Design 风格
    提供用户管理和分类管理功能，具有现代化的选项卡界面
    可嵌入到 NavigationInterface 中使用
    """
    
    # 定义信号，当分类更新时发出
    categories_updated = pyqtSignal()
    
    def __init__(self, user_id=1, username="admin", sound_manager=None, parent=None):
        """
        初始化设置页面
        
        Args:
            user_id (int): 当前用户ID
            username (str): 当前用户名
            sound_manager: 声音管理器实例
            parent: 父控件
        """
        super().__init__(parent)
        self.user_id = user_id
        self.username = username
        self.sound_manager = sound_manager
        self.category_inputs = []  # 存储分类输入框
        
        self.init_ui()
        self.load_users()
        self.load_categories()
    
    def init_ui(self):
        """
        初始化用户界面
        """
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 15, 20, 15)
        
        # 创建标题
        self.create_title_area(main_layout)
        
        # 创建选项卡容器
        from PyQt6.QtWidgets import QStackedWidget
        self.stacked_widget = QStackedWidget()
        
        # 创建选项卡切换器
        self.tab_selector = SegmentedWidget()
        self.tab_selector.addItem("user_management", "用户管理")
        self.tab_selector.addItem("category_management", "分类管理")
        self.tab_selector.addItem("api_management", "API配置")
        self.tab_selector.setFixedHeight(40)
        self.tab_selector.currentItemChanged.connect(self.on_tab_changed)
        
        # 连接选项卡切换音效
        if self.sound_manager:
            self.tab_selector.currentItemChanged.connect(lambda: self.sound_manager.play_click())
        
        main_layout.addWidget(self.tab_selector, 0, Qt.AlignmentFlag.AlignCenter)
        
        # 创建用户管理选项卡
        self.create_user_management_tab()
        
        # 创建分类管理选项卡
        self.create_category_management_tab()
        
        # 创建API管理选项卡
        self.create_api_management_tab()
        
        main_layout.addWidget(self.stacked_widget)
        
        # 设置默认选中
        self.tab_selector.setCurrentItem("user_management")
        self.stacked_widget.setCurrentIndex(0)
    
    def create_title_area(self, parent_layout):
        """
        创建紧凑的标题区域
        """
        title_card = CardWidget()
        title_layout = QHBoxLayout(title_card)
        title_layout.setContentsMargins(20, 10, 20, 10)
        title_layout.setSpacing(15)
        
        # 主标题（缩小字体）
        main_title = SubtitleLabel("系统设置 /  تەڭشەك")
        
        title_layout.addWidget(main_title)
        title_layout.addStretch()
        
        parent_layout.addWidget(title_card)
    
    def create_user_management_tab(self):
        """
        创建用户管理选项卡
        """
        user_tab = QWidget()
        user_layout = QVBoxLayout(user_tab)
        user_layout.setSpacing(15)
        user_layout.setContentsMargins(15, 15, 15, 15)
        
        # 修改密码区域
        password_card = CardWidget()
        password_layout = QVBoxLayout(password_card)
        password_layout.setSpacing(15)
        password_layout.setContentsMargins(20, 15, 20, 15)
        
        password_title = SubtitleLabel("修改密码")
        password_layout.addWidget(password_title)
        
        # 密码输入区域（优化为水平布局）
        password_grid = QHBoxLayout()
        password_grid.setSpacing(15)
        
        # 第一列：当前密码
        col1_layout = QVBoxLayout()
        col1_layout.setSpacing(8)
        current_password_label = BodyLabel("当前密码:")
        self.current_password_input = PasswordLineEdit()
        self.current_password_input.setPlaceholderText("请输入当前密码")
        self.current_password_input.setFixedWidth(180)
        col1_layout.addWidget(current_password_label)
        col1_layout.addWidget(self.current_password_input)
        
        # 第二列：新密码
        col2_layout = QVBoxLayout()
        col2_layout.setSpacing(8)
        new_password_label = BodyLabel("新密码:")
        self.new_password_input = PasswordLineEdit()
        self.new_password_input.setPlaceholderText("请输入新密码")
        self.new_password_input.setFixedWidth(180)
        col2_layout.addWidget(new_password_label)
        col2_layout.addWidget(self.new_password_input)
        
        # 第三列：确认密码
        col3_layout = QVBoxLayout()
        col3_layout.setSpacing(8)
        confirm_password_label = BodyLabel("确认密码:")
        self.confirm_password_input = PasswordLineEdit()
        self.confirm_password_input.setPlaceholderText("请再次输入新密码")
        self.confirm_password_input.setFixedWidth(180)
        col3_layout.addWidget(confirm_password_label)
        col3_layout.addWidget(self.confirm_password_input)
        
        password_grid.addLayout(col1_layout)
        password_grid.addLayout(col2_layout)
        password_grid.addLayout(col3_layout)
        password_grid.addStretch()
        
        password_layout.addLayout(password_grid)
        
        # 修改密码按钮
        change_password_btn = PrimaryPushButton("修改密码")
        change_password_btn.setMinimumHeight(35)
        change_password_btn.setMinimumWidth(160)
        change_password_btn.clicked.connect(self.change_password)
        
        # 连接修改密码按钮音效
        if self.sound_manager:
            change_password_btn.clicked.connect(self.sound_manager.play_confirmation)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(change_password_btn)
        button_layout.addStretch()
        password_layout.addLayout(button_layout)
        
        user_layout.addWidget(password_card)
        
        # 用户管理区域（仅管理员可见）
        if self.username == "admin":
            user_mgmt_card = CardWidget()
            user_mgmt_layout = QVBoxLayout(user_mgmt_card)
            user_mgmt_layout.setSpacing(15)
            user_mgmt_layout.setContentsMargins(20, 15, 20, 15)
            
            user_mgmt_title = SubtitleLabel("用户管理")
            user_mgmt_layout.addWidget(user_mgmt_title)
            
            # 水平布局：添加用户区域和用户列表
            horizontal_layout = QHBoxLayout()
            horizontal_layout.setSpacing(20)
            
            # 左侧：添加用户区域（紧凑版）
            add_user_card = CardWidget()
            add_user_layout = QVBoxLayout(add_user_card)
            add_user_layout.setContentsMargins(15, 15, 15, 15)
            add_user_layout.setSpacing(10)
            
            add_user_title = BodyLabel("添加新用户")
            add_user_layout.addWidget(add_user_title)
            
            # 用户输入区域（垂直紧凑布局）
            username_label = BodyLabel("用户名:")
            self.new_username_input = LineEdit()
            self.new_username_input.setPlaceholderText("输入新用户名")
            self.new_username_input.setFixedWidth(220)
            
            password_label = BodyLabel("密码:")
            self.new_user_password_input = PasswordLineEdit()
            self.new_user_password_input.setPlaceholderText("输入密码")
            self.new_user_password_input.setFixedWidth(220)
            
            add_user_layout.addWidget(username_label)
            add_user_layout.addWidget(self.new_username_input)
            add_user_layout.addWidget(password_label)
            add_user_layout.addWidget(self.new_user_password_input)
            
            # 添加用户按钮
            add_user_btn = PushButton("添加用户")
            add_user_btn.setMinimumHeight(32)
            add_user_btn.setFixedWidth(160)
            add_user_btn.setStyleSheet("background-color: #1A5319; color: white; border: none; border-radius: 6px;")
            add_user_btn.clicked.connect(self.add_user)
            
            # 连接添加用户按钮音效
            if self.sound_manager:
                add_user_btn.clicked.connect(self.sound_manager.play_confirmation)
            
            add_user_layout.addWidget(add_user_btn)
            add_user_layout.addStretch()
            
            # 右侧：用户列表区域
            users_list_card = CardWidget()
            users_list_layout = QVBoxLayout(users_list_card)
            users_list_layout.setContentsMargins(15, 15, 15, 15)
            users_list_layout.setSpacing(10)
            
            users_list_title = BodyLabel("现有用户列表")
            users_list_layout.addWidget(users_list_title)
            
            self.users_scroll = ScrollArea()
            self.users_scroll.setMinimumHeight(200)
            self.users_scroll.setMaximumHeight(250)
            self.users_scroll.setWidgetResizable(True)
            self.users_scroll.setStyleSheet("""
                ScrollArea { 
                    background-color: #FAFBFA; 
                    border: 1px solid #D0E8D0; 
                    border-radius: 6px;
                }
            """)
            
            self.users_widget = QWidget()
            self.users_widget.setStyleSheet("QWidget { background-color: #FAFBFA; }")
            self.users_layout = QVBoxLayout(self.users_widget)
            self.users_layout.setSpacing(10)
            self.users_layout.setContentsMargins(10, 10, 10, 10)
            self.users_scroll.setWidget(self.users_widget)
            
            users_list_layout.addWidget(self.users_scroll)
            
            # 设置左右比例
            horizontal_layout.addWidget(add_user_card, 1)  # 添加用户区域 
            horizontal_layout.addWidget(users_list_card, 2)  # 用户列表区域占更多空间
            
            user_mgmt_layout.addLayout(horizontal_layout)
            user_layout.addWidget(user_mgmt_card)
        
        user_layout.addStretch()
        self.stacked_widget.addWidget(user_tab)
    
    def create_category_management_tab(self):
        """
        创建分类管理选项卡
        """
        category_tab = QWidget()
        category_layout = QVBoxLayout(category_tab)
        category_layout.setSpacing(15)
        category_layout.setContentsMargins(15, 15, 15, 15)
        
        # 水平布局：添加分类区域和分类列表
        horizontal_layout = QHBoxLayout()
        horizontal_layout.setSpacing(20)
        
        # 左侧：添加分类区域（紧凑版）
        add_category_card = CardWidget()
        add_category_layout = QVBoxLayout(add_category_card)
        add_category_layout.setSpacing(15)
        add_category_layout.setContentsMargins(20, 15, 20, 15)
        
        add_category_title = SubtitleLabel("添加新分类")
        add_category_layout.addWidget(add_category_title)
        
        # 分类输入区域（垂直紧凑布局）
        cn_name_label = BodyLabel("中文名称:")
        self.category_cn_input = LineEdit()
        self.category_cn_input.setPlaceholderText("输入中文分类名称")
        self.category_cn_input.setFixedWidth(280)
        
        ug_name_label = BodyLabel("维语名称:")
        self.category_ug_input = LineEdit()
        self.category_ug_input.setPlaceholderText("输入维语分类名称")
        self.category_ug_input.setFixedWidth(280)
        
        emoji_label = BodyLabel("表情图标:")
        self.category_emoji_input = LineEdit()
        self.category_emoji_input.setPlaceholderText("输入表情图标 (如: 🐄 🐑 🐔)")
        self.category_emoji_input.setFixedWidth(280)
        
        add_category_layout.addWidget(cn_name_label)
        add_category_layout.addWidget(self.category_cn_input)
        add_category_layout.addWidget(ug_name_label)
        add_category_layout.addWidget(self.category_ug_input)
        add_category_layout.addWidget(emoji_label)
        add_category_layout.addWidget(self.category_emoji_input)
        
        # 添加分类按钮
        add_category_btn = PrimaryPushButton("添加分类")
        add_category_btn.setMinimumHeight(35)
        add_category_btn.setFixedWidth(160)
        add_category_btn.clicked.connect(self.add_category)
        
        # 连接添加分类按钮音效
        if self.sound_manager:
            add_category_btn.clicked.connect(self.sound_manager.play_confirmation)
        add_category_layout.addWidget(add_category_btn)
        add_category_layout.addStretch()
        
        # 右侧：分类列表区域
        categories_list_card = CardWidget()
        categories_list_layout = QVBoxLayout(categories_list_card)
        categories_list_layout.setContentsMargins(20, 15, 20, 15)
        categories_list_layout.setSpacing(15)
        
        categories_list_title = SubtitleLabel("现有分类列表")
        categories_list_layout.addWidget(categories_list_title)
        
        # 分类滚动区域
        self.categories_scroll = ScrollArea()
        self.categories_scroll.setMinimumHeight(350)
        self.categories_scroll.setWidgetResizable(True)
        self.categories_scroll.setStyleSheet("""
            ScrollArea { 
                background-color: #FAFBFA; 
                border: 1px solid #D0E8D0; 
                border-radius: 6px;
            }
        """)
        
        self.categories_widget = QWidget()
        self.categories_widget.setStyleSheet("QWidget { background-color: #FAFBFA; }")
        self.categories_layout = QVBoxLayout(self.categories_widget)
        self.categories_layout.setSpacing(12)
        self.categories_layout.setContentsMargins(12, 12, 12, 12)
        self.categories_scroll.setWidget(self.categories_widget)
        
        categories_list_layout.addWidget(self.categories_scroll)
        
        # 设置左右比例
        horizontal_layout.addWidget(add_category_card, 1)  # 添加分类区域
        horizontal_layout.addWidget(categories_list_card, 2)  # 分类列表区域占更多空间
        
        category_layout.addLayout(horizontal_layout)
        category_layout.addStretch()
        self.stacked_widget.addWidget(category_tab)
    
    def on_tab_changed(self, key):
        """
        处理选项卡切换
        
        Args:
            key (str): 选项卡键值
        """
        if key == "user_management":
            index = 0
        elif key == "category_management":
            index = 1
        elif key == "api_management":
            index = 2
        else:
            index = 0
        self.stacked_widget.setCurrentIndex(index)
    
    def load_users(self):
        """
        加载用户数据
        """
        if self.username != "admin":
            return
            
        # 检查是否有用户布局属性（非admin用户可能没有）
        if not hasattr(self, 'users_layout') or self.users_layout is None:
            return
            
        try:
            # 清空现有用户列表
            for i in reversed(range(self.users_layout.count())):
                child = self.users_layout.itemAt(i).widget()
                if child:
                    child.setParent(None)
            
            # 获取用户数据
            users = get_all_users()
            
            for user in users:
                user_id, username = user
                
                # 创建用户项
                user_card = CardWidget()
                user_card.setMaximumHeight(85)
                user_card.setStyleSheet("""
                    CardWidget {
                        background-color: #FFFFFF;
                        border: 1px solid #E0E0E0;
                        border-radius: 6px;
                    }
                    CardWidget:hover {
                        background-color: #F8FDF8;
                        border-color: #1A5319;
                    }
                """)
                user_item_layout = QHBoxLayout(user_card)
                user_item_layout.setContentsMargins(18, 12, 18, 12)
                user_item_layout.setSpacing(15)
                
                # 用户信息
                user_info_label = BodyLabel(f"用户ID: {user_id}  |  用户名: {username}")
                user_info_label.setMinimumWidth(200)
                user_info_label.setStyleSheet("color: #333333; font-size: 13px; font-weight: 500;")
                
                # 删除按钮（不能删除admin和当前用户）
                if username != "admin" and user_id != self.user_id:
                    delete_user_btn = PushButton("删除")
                    delete_user_btn.setMaximumHeight(32)
                    delete_user_btn.setMaximumWidth(80)
                    delete_user_btn.setStyleSheet("""
                        PushButton {
                            background-color: #DC3545;
                            color: white;
                            border: none;
                            border-radius: 6px;
                            font-size: 12px;
                            font-weight: 500;
                        }
                        PushButton:hover {
                            background-color: #C82333;
                        }
                        PushButton:pressed {
                            background-color: #A71E2A;
                        }
                    """)
                    delete_user_btn.clicked.connect(lambda checked, uid=user_id, uname=username: self.delete_user(uid, uname))
                    
                    # 连接删除用户按钮音效
                    if self.sound_manager:
                        delete_user_btn.clicked.connect(self.sound_manager.play_warning)
                    
                    user_item_layout.addWidget(user_info_label)
                    user_item_layout.addStretch()
                    user_item_layout.addWidget(delete_user_btn)
                else:
                    status_label = BodyLabel("(系统管理员 / سىستېما باشقۇرغۇچىسى)" if username == "admin" else "(当前用户 / ھازىرقى ئىشلەتكۈچى)")
                    status_label.setStyleSheet("color: #666666; font-size: 12px; font-style: italic;")
                    user_item_layout.addWidget(user_info_label)
                    user_item_layout.addStretch()
                    user_item_layout.addWidget(status_label)
                
                self.users_layout.addWidget(user_card)
                
        except Exception as e:
            InfoBar.error(
                title="加载失败",
                content=f"无法加载用户数据：{str(e)}\nئىشلەتكۈچى مەلۇماتىنى يۈكلىيەلمىدى: {str(e)}",
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def load_categories(self):
        """
        加载分类数据
        """
        # 检查是否有分类布局属性
        if not hasattr(self, 'categories_layout') or self.categories_layout is None:
            return
            
        try:
            # 清空现有分类列表
            for i in reversed(range(self.categories_layout.count())):
                child = self.categories_layout.itemAt(i).widget()
                if child:
                    child.setParent(None)
            
            # 清空输入框列表
            self.category_inputs.clear()
            
            # 获取分类数据
            categories = get_all_categories()
            
            for category in categories:
                category_id = category['id']
                name_cn = category['name_cn']
                name_ug = category['name_ug']
                emoji = category.get('emoji', '📝')
                
                # 创建分类项
                category_card = CardWidget()
                category_card.setMaximumHeight(110)
                category_card.setStyleSheet("""
                    CardWidget {
                        background-color: #FFFFFF;
                        border: 1px solid #E0E0E0;
                        border-radius: 6px;
                    }
                    CardWidget:hover {
                        background-color: #F8FDF8;
                        border-color: #1A5319;
                    }
                """)
                category_item_layout = QVBoxLayout(category_card)
                category_item_layout.setContentsMargins(18, 12, 18, 12)
                category_item_layout.setSpacing(10)
                
                # 分类信息和操作按钮行
                info_layout = QHBoxLayout()
                info_layout.setSpacing(15)
                
                # 分类信息
                category_info = BodyLabel(f"ID: {category_id}")
                category_info.setMinimumWidth(60)
                category_info.setFixedWidth(60)
                category_info.setStyleSheet("color: #333333; font-size: 13px; font-weight: 600;")
                
                # 中文名称输入框
                cn_input = LineEdit()
                cn_input.setText(name_cn)
                cn_input.setMinimumWidth(150)
                cn_input.setMaximumWidth(200)
                cn_input.setStyleSheet("""
                    LineEdit {
                        background-color: #FAFAFA;
                        border: 1px solid #CCCCCC;
                        border-radius: 4px;
                        padding: 6px 10px;
                        color: #333333;
                        font-size: 13px;
                    }
                    LineEdit:focus {
                        border-color: #1A5319;
                        background-color: #FFFFFF;
                    }
                """)
                
                # 维语名称输入框
                ug_input = LineEdit()
                ug_input.setText(name_ug)
                ug_input.setMinimumWidth(150)
                ug_input.setMaximumWidth(200)
                ug_input.setStyleSheet("""
                    LineEdit {
                        background-color: #FAFAFA;
                        border: 1px solid #CCCCCC;
                        border-radius: 4px;
                        padding: 6px 10px;
                        color: #333333;
                        font-size: 13px;
                    }
                    LineEdit:focus {
                        border-color: #1A5319;
                        background-color: #FFFFFF;
                    }
                """)
                
                # 表情输入框
                emoji_input = LineEdit()
                emoji_input.setText(emoji)
                emoji_input.setMinimumWidth(80)
                emoji_input.setMaximumWidth(100)
                emoji_input.setStyleSheet("""
                    LineEdit {
                        background-color: #FAFAFA;
                        border: 1px solid #CCCCCC;
                        border-radius: 4px;
                        padding: 6px 10px;
                        color: #333333;
                        font-size: 16px;
                        text-align: center;
                    }
                    LineEdit:focus {
                        border-color: #1A5319;
                        background-color: #FFFFFF;
                    }
                """)
                
                # 保存这些输入框的引用
                self.category_inputs.append({
                    'id': category_id,
                    'cn_input': cn_input,
                    'ug_input': ug_input,
                    'emoji_input': emoji_input
                })
                
                # 更新按钮
                update_btn = PushButton("更新")
                update_btn.setMaximumHeight(32)
                update_btn.setMinimumWidth(80)
                update_btn.setMaximumWidth(120)
                update_btn.setStyleSheet("""
                    PushButton {
                        background-color: #1A5319;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-size: 13px;
                        font-weight: 500;
                        padding: 6px 12px;
                    }
                    PushButton:hover {
                        background-color: #2A6B29;
                    }
                    PushButton:pressed {
                        background-color: #0F3E0E;
                    }
                """)
                update_btn.clicked.connect(lambda checked, cid=category_id: self.update_category(cid))
                
                # 连接更新按钮音效
                if self.sound_manager:
                    update_btn.clicked.connect(self.sound_manager.play_confirmation)
                
                # 删除按钮
                delete_btn = PushButton("删除")
                delete_btn.setMaximumHeight(32)
                delete_btn.setMinimumWidth(80)
                delete_btn.setMaximumWidth(120)
                delete_btn.setStyleSheet("""
                    PushButton {
                        background-color: #DC3545;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-size: 13px;
                        font-weight: 500;
                        padding: 6px 12px;
                    }
                    PushButton:hover {
                        background-color: #C82333;
                    }
                    PushButton:pressed {
                        background-color: #A71E2A;
                    }
                """)
                delete_btn.clicked.connect(lambda checked, cid=category_id, cname=name_cn: self.delete_category(cid, cname))
                
                # 连接删除分类按钮音效
                if self.sound_manager:
                    delete_btn.clicked.connect(self.sound_manager.play_warning)
                
                info_layout.addWidget(category_info)
                info_layout.addWidget(cn_input)
                info_layout.addWidget(ug_input)
                info_layout.addWidget(emoji_input)
                info_layout.addStretch()
                info_layout.addWidget(update_btn)
                info_layout.addWidget(delete_btn)
                
                category_item_layout.addLayout(info_layout)
                
                # 标签行
                labels_layout = QHBoxLayout()
                labels_layout.setSpacing(15)
                
                id_spacer = QWidget()
                id_spacer.setMinimumWidth(60)
                id_spacer.setFixedWidth(60)
                
                cn_label = BodyLabel("中文名称")
                cn_label.setMinimumWidth(150)
                cn_label.setMaximumWidth(200)
                cn_label.setStyleSheet("color: #333333; font-size: 12px; font-weight: 600;")
                
                ug_label = BodyLabel("维语名称")
                ug_label.setMinimumWidth(150)
                ug_label.setMaximumWidth(200)
                ug_label.setStyleSheet("color: #333333; font-size: 12px; font-weight: 600;")
                
                emoji_label = BodyLabel("表情")
                emoji_label.setMinimumWidth(80)
                emoji_label.setMaximumWidth(100)
                emoji_label.setStyleSheet("color: #333333; font-size: 12px; font-weight: 600;")
                
                labels_layout.addWidget(id_spacer)
                labels_layout.addWidget(cn_label)
                labels_layout.addWidget(ug_label)
                labels_layout.addWidget(emoji_label)
                labels_layout.addStretch()
                
                category_item_layout.addLayout(labels_layout)
                
                self.categories_layout.addWidget(category_card)
                
        except Exception as e:
            InfoBar.error(
                title="加载失败",
                content=f"无法加载分类数据：{str(e)}\nتۈر مەلۇماتىنى يۈكلىيەلمىدى: {str(e)}",
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def change_password(self):
        """
        修改密码
        """
        try:
            current_pwd = self.current_password_input.text().strip()
            new_pwd = self.new_password_input.text().strip()
            confirm_pwd = self.confirm_password_input.text().strip()
            
            # 验证输入
            if not all([current_pwd, new_pwd, confirm_pwd]):
                InfoBar.warning(
                    title="输入错误",
                    content="请填写所有密码字段\nبارلىق مەخپىي نومۇر رامكىسىنى تولدۇرۇڭ",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                return
                
            if new_pwd != confirm_pwd:
                InfoBar.warning(
                    title="密码不匹配",
                    content="新密码和确认密码不匹配\nيېڭى مەخپىي نومۇر ۋە جەزملەش مەخپىي نومۇرى ماس كەلمىدى",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                return
                
            if len(new_pwd) < 4:
                InfoBar.warning(
                    title="密码过短",
                    content="密码长度至少4位\nمەخپىي نومۇر ئۇزۇنلۇقى كەم دېگەندە 4 خانە",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                return
            
            # 执行密码修改
            success = update_user_credentials(self.user_id, current_pwd, new_password=new_pwd)
            
            if success:
                InfoBar.success(
                    title="修改成功",
                    content="密码修改成功\nمەخپىي نومۇر ئۆزگەرتىش مۇۋەپپەقىيەتلىك",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                
                # 清空输入框
                self.current_password_input.clear()
                self.new_password_input.clear()
                self.confirm_password_input.clear()
            else:
                InfoBar.error(
                    title="修改失败",
                    content="当前密码错误或其他错误\nھازىرقى مەخپىي نومۇر خاتا ياكى باشقا خاتالىق",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                
        except Exception as e:
            InfoBar.error(
                title="修改失败",
                content=f"密码修改失败：{str(e)}\nمەخپىي نومۇر ئۆزگەرتىش مەغلۇب بولدى: {str(e)}",
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def add_user(self):
        """
        添加用户
        """
        if self.username != "admin":
            return
            
        try:
            username = self.new_username_input.text().strip()
            password = self.new_user_password_input.text().strip()
            
            # 验证输入
            if not username or not password:
                InfoBar.warning(
                    title="输入错误",
                    content="请填写用户名和密码\nئىشلەتكۈچى نامى ۋە مەخپىي نومۇرنى تولدۇرۇڭ",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                return
                
            if len(username) < 3:
                InfoBar.warning(
                    title="用户名过短",
                    content="用户名长度至少3位\nئىشلەتكۈچى نامى ئۇزۇنلۇقى كەم دېگەندە 3 خانە",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                return
                
            if len(password) < 4:
                InfoBar.warning(
                    title="密码过短",
                    content="密码长度至少4位\nمەخپىي نومۇر ئۇزۇنلۇقى كەم دېگەندە 4 خانە",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                return
            
            # 执行添加
            success = add_user(username, password)
            
            if success:
                InfoBar.success(
                    title="添加成功",
                    content=f"用户 {username} 添加成功\nئىشلەتكۈچى {username} قوشۇش مۇۋەپپەقىيەتلىك",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                
                # 清空输入框
                self.new_username_input.clear()
                self.new_user_password_input.clear()
                
                # 重新加载用户列表
                self.load_users()
            else:
                InfoBar.error(
                    title="添加失败",
                    content="用户添加失败，可能用户名已存在\nئىشلەتكۈچى قوشۇش مەغلۇب بولدى، ئىشلەتكۈچى نامى مەۋجۇت بولۇشى مۇمكىن",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                
        except Exception as e:
            InfoBar.error(
                title="添加失败",
                content=f"用户添加失败：{str(e)}\nئىشلەتكۈچى قوشۇش مەغلۇب بولدى: {str(e)}",
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def delete_user(self, user_id, username):
        """
        删除用户
        
        Args:
            user_id (int): 用户ID
            username (str): 用户名
        """
        if self.username != "admin":
            return
            
        try:
            # 确认删除
            reply = MessageBox(
                "确认删除",
                f"确定要删除用户 {username} 吗？\n{username} ئىشلەتكۈچىسىنى راستىنلا ئۆچۈرەمسىز؟",
                self
            )
            reply.yesButton.setText("确定")
            reply.cancelButton.setText("取消")
            
            if reply.exec():
                # 执行删除
                success = delete_user(user_id)
                
                if success:
                    InfoBar.success(
                        title="删除成功",
                        content=f"用户 {username} 删除成功\nئىشلەتكۈچى {username} ئۆچۈرۈش مۇۋەپپەقىيەتلىك",
                        duration=3000,
                        position=InfoBarPosition.TOP,
                        parent=self
                    )
                    
                    # 重新加载用户列表
                    self.load_users()
                else:
                    InfoBar.error(
                        title="删除失败",
                        content="用户删除失败\nئىشلەتكۈچى ئۆچۈرۈش مەغلۇب بولدى",
                        duration=3000,
                        position=InfoBarPosition.TOP,
                        parent=self
                    )
                    
        except Exception as e:
            InfoBar.error(
                title="删除失败",
                content=f"用户删除失败：{str(e)}\nئىشلەتكۈچى ئۆچۈرۈش مەغلۇب بولدى: {str(e)}",
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def add_category(self):
        """
        添加分类
        """
        try:
            name_cn = self.category_cn_input.text().strip()
            name_ug = self.category_ug_input.text().strip()
            emoji = self.category_emoji_input.text().strip()
            
            # 验证输入
            if not name_cn or not name_ug:
                InfoBar.warning(
                    title="输入错误",
                    content="请填写中文和维语分类名称\nخەنزۇچە ۋە ئۇيغۇرچە تۈر نامىنى تولدۇرۇڭ",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                return
            
            # 如果没有输入表情，使用默认表情
            if not emoji:
                emoji = '📝'
            
            # 执行添加
            success, message, category_id = add_category(name_cn, name_ug, emoji)
            
            if success:
                InfoBar.success(
                    title="添加成功",
                    content=f"分类 {name_cn} / {name_ug} 添加成功\nتۈر {name_cn} / {name_ug} قوشۇش مۇۋەپپەقىيەتلىك",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                
                # 清空输入框
                self.category_cn_input.clear()
                self.category_ug_input.clear()
                self.category_emoji_input.clear()
                
                # 重新加载分类列表
                self.load_categories()
                
                # 发出分类更新信号
                self.categories_updated.emit()
            else:
                InfoBar.error(
                    title="添加失败",
                    content="分类添加失败，可能分类已存在\nتۈر قوشۇش مەغلۇب بولدى، تۈر مەۋجۇت بولۇشى مۇمكىن",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                
        except Exception as e:
            InfoBar.error(
                title="添加失败",
                content=f"分类添加失败：{str(e)}\nتۈر قوشۇش مەغلۇب بولدى: {str(e)}",
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def update_category(self, category_id):
        """
        更新分类
        
        Args:
            category_id (int): 分类ID
        """
        try:
            # 找到对应的输入框
            category_input = None
            for item in self.category_inputs:
                if item['id'] == category_id:
                    category_input = item
                    break
            
            if not category_input:
                return
            
            name_cn = category_input['cn_input'].text().strip()
            name_ug = category_input['ug_input'].text().strip()
            emoji = category_input['emoji_input'].text().strip()
            
            # 验证输入
            if not name_cn or not name_ug:
                InfoBar.warning(
                    title="输入错误",
                    content="请填写中文和维语分类名称\nخەنزۇچە ۋە ئۇيغۇرچە تۈر نامىنى تولدۇرۇڭ",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                return
            
            # 如果没有输入表情，使用默认表情
            if not emoji:
                emoji = '📝'
            
            # 调用更新分类的模型函数
            success, message = update_category(category_id, name_cn, name_ug, emoji)
            
            if success:
                InfoBar.success(
                    title="更新成功",
                    content=message,
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                
                # 重新加载分类列表
                self.load_categories()
                
                # 发出分类更新信号
                self.categories_updated.emit()
            else:
                InfoBar.error(
                    title="更新失败",
                    content=message,
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
            
        except Exception as e:
            InfoBar.error(
                title="更新失败",
                content=f"分类更新失败：{str(e)}\nتۈر يېڭىلاش مەغلۇب بولدى: {str(e)}",
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def delete_category(self, category_id, category_name):
        """
        删除分类
        
        Args:
            category_id (int): 分类ID
            category_name (str): 分类名称
        """
        try:
            # 确认删除
            reply = MessageBox(
                "确认删除",
                f"确定要删除分类 {category_name} 吗？\n{category_name} تۈرىنى راستىنلا ئۆچۈرەمسىز؟",
                self
            )
            reply.yesButton.setText("确定")
            reply.cancelButton.setText("取消")
            
            if reply.exec():
                # 执行删除
                success = delete_category(category_id)
                
                if success:
                    InfoBar.success(
                        title="删除成功",
                        content=f"分类 {category_name} 删除成功\nتۈر {category_name} ئۆچۈرۈش مۇۋەپپەقىيەتلىك",
                        duration=3000,
                        position=InfoBarPosition.TOP,
                        parent=self
                    )
                    
                    # 重新加载分类列表
                    self.load_categories()
                    
                    # 发出分类更新信号
                    self.categories_updated.emit()
                else:
                    InfoBar.error(
                        title="删除失败",
                        content="分类删除失败，可能该分类下有支出记录\nتۈر ئۆچۈرۈش مەغلۇب بولدى، بۇ تۈر ئاستىدا چىقىم خاتىرىسى بولۇشى مۇمكىن",
                        duration=3000,
                        position=InfoBarPosition.TOP,
                        parent=self
                    )
                    
        except Exception as e:
            InfoBar.error(
                title="删除失败",
                content=f"分类删除失败：{str(e)}\nتۈر ئۆچۈرۈش مەغلۇب بولدى: {str(e)}",
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def create_api_management_tab(self):
        """
        创建API管理选项卡
        """
        api_tab = QWidget()
        api_layout = QVBoxLayout(api_tab)
        api_layout.setSpacing(15)
        api_layout.setContentsMargins(15, 15, 15, 15)
        
        # DeepSeek API配置区域
        api_card = CardWidget()
        api_card_layout = QVBoxLayout(api_card)
        api_card_layout.setSpacing(20)
        api_card_layout.setContentsMargins(25, 20, 25, 20)
        
        # 标题
        api_title = SubtitleLabel("DeepSeek API 配置")
        api_card_layout.addWidget(api_title)
        
        # 当前API状态区域
        status_layout = QHBoxLayout()
        status_layout.setSpacing(15)
        
        # 状态显示
        self.api_status_label = BodyLabel("API状态: 未配置")
        self.api_status_label.setStyleSheet("""
            BodyLabel {
                color: #DC3545;
                font-size: 14px;
                font-weight: 500;
                padding: 8px 12px;
                background-color: #F8D7DA;
                border: 1px solid #F5C6CB;
                border-radius: 6px;
            }
        """)
        
        # API显示（显示后四位）
        self.api_display_label = BodyLabel("当前API: 未设置")
        self.api_display_label.setStyleSheet("""
            BodyLabel {
                color: #495057;
                font-size: 13px;
                padding: 8px 12px;
                background-color: #F8F9FA;
                border: 1px solid #DEE2E6;
                border-radius: 6px;
                font-family: 'Courier New', monospace;
            }
        """)
        
        status_layout.addWidget(self.api_status_label)
        status_layout.addWidget(self.api_display_label)
        status_layout.addStretch()
        
        api_card_layout.addLayout(status_layout)
        
        # 操作区域
        operation_layout = QVBoxLayout()
        operation_layout.setSpacing(15)
        
        # 输入新API密钥区域
        input_section = CardWidget()
        input_section.setStyleSheet("CardWidget { background-color: #F8FDF8; border: 1px solid #D1F2D1; }")
        input_layout = QVBoxLayout(input_section)
        input_layout.setSpacing(12)
        input_layout.setContentsMargins(20, 15, 20, 15)
        
        input_title = BodyLabel("设置新API密钥")
        input_title.setStyleSheet("color: #1A5319; font-weight: 600;")
        input_layout.addWidget(input_title)
        
        # API输入框
        api_input_layout = QHBoxLayout()
        api_input_layout.setSpacing(10)
        
        self.api_input = LineEdit()
        self.api_input.setPlaceholderText("请输入DeepSeek API密钥 (格式: sk-...)")
        self.api_input.setMinimumHeight(35)
        self.api_input.setStyleSheet("""
            LineEdit {
                background-color: #FFFFFF;
                border: 2px solid #CED4DA;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                font-family: 'Courier New', monospace;
            }
            LineEdit:focus {
                border-color: #1A5319;
                background-color: #FFFFFF;
            }
        """)
        
        # 保存按钮
        save_api_btn = PrimaryPushButton("保存API密钥")
        save_api_btn.setMinimumHeight(35)
        save_api_btn.setMinimumWidth(130)
        save_api_btn.clicked.connect(self.save_api_key)
        
        # 连接保存按钮音效
        if self.sound_manager:
            save_api_btn.clicked.connect(self.sound_manager.play_confirmation)
        
        api_input_layout.addWidget(self.api_input)
        api_input_layout.addWidget(save_api_btn)
        
        input_layout.addLayout(api_input_layout)
        
        # 提示信息
        tip_label = BodyLabel("💡 提示：API密钥可在DeepSeek官网(https://deepseek.com)获取，格式通常为sk开头")
        tip_label.setStyleSheet("color: #6C757D; font-size: 12px; font-style: italic;")
        input_layout.addWidget(tip_label)
        
        operation_layout.addWidget(input_section)
        
        # 操作按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # 删除API按钮
        self.delete_api_btn = PushButton("删除当前API")
        self.delete_api_btn.setMinimumHeight(35)
        self.delete_api_btn.setMinimumWidth(130)
        self.delete_api_btn.setStyleSheet("""
            PushButton {
                background-color: #DC3545;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 500;
            }
            PushButton:hover {
                background-color: #C82333;
            }
            PushButton:pressed {
                background-color: #A71E2A;
            }
        """)
        self.delete_api_btn.clicked.connect(self.delete_api_key)
        
        # 测试连接按钮
        test_api_btn = PushButton("测试连接")
        test_api_btn.setMinimumHeight(35)
        test_api_btn.setMinimumWidth(110)
        test_api_btn.setStyleSheet("""
            PushButton {
                background-color: #17A2B8;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 500;
            }
            PushButton:hover {
                background-color: #138496;
            }
            PushButton:pressed {
                background-color: #0F6674;
            }
        """)
        test_api_btn.clicked.connect(self.test_api_connection)
        
        # 连接按钮音效
        if self.sound_manager:
            self.delete_api_btn.clicked.connect(self.sound_manager.play_warning)
            test_api_btn.clicked.connect(self.sound_manager.play_click)
        
        button_layout.addWidget(self.delete_api_btn)
        button_layout.addWidget(test_api_btn)
        button_layout.addStretch()
        
        operation_layout.addLayout(button_layout)
        
        api_card_layout.addLayout(operation_layout)
        
        api_layout.addWidget(api_card)
        api_layout.addStretch()
        
        self.stacked_widget.addWidget(api_tab)
        
        # 加载当前API状态
        self.load_api_status()
    
    def get_config_path(self):
        """
        获取配置文件路径
        在用户数据目录中存储配置文件，避免打包问题
        """
        # 获取用户数据目录
        if sys.platform == "win32":
            # Windows: 使用APPDATA目录
            app_data = os.environ.get('APPDATA')
            if app_data:
                app_dir = os.path.join(app_data, 'NilufarRestaurant')
            else:
                app_dir = os.path.expanduser('~/.nilufar_restaurant')
        else:
            # Linux/macOS: 使用用户主目录
            app_dir = os.path.expanduser('~/.nilufar_restaurant')
        
        # 确保目录存在
        if not os.path.exists(app_dir):
            os.makedirs(app_dir, exist_ok=True)
        
        return os.path.join(app_dir, 'config.ini')
    
    def load_api_status(self):
        """
        加载并显示当前API状态
        """
        try:
            config_path = self.get_config_path()
            
            if not os.path.exists(config_path):
                # 创建默认配置文件
                self.create_default_config(config_path)
                self.api_status_label.setText("API状态: 未配置")
                self.api_status_label.setStyleSheet("""
                    BodyLabel {
                        color: #DC3545;
                        font-size: 14px;
                        font-weight: 500;
                        padding: 8px 12px;
                        background-color: #F8D7DA;
                        border: 1px solid #F5C6CB;
                        border-radius: 6px;
                    }
                """)
                self.api_display_label.setText("当前API: 未设置")
                self.delete_api_btn.setEnabled(False)
                return
            
            config = configparser.ConfigParser()
            # 保持选项名大小写
            config.optionxform = str
            try:
                config.read(config_path, encoding='utf-8')
            except configparser.Error:
                # 如果配置文件格式错误，重新创建
                self.create_default_config(config_path)
                config.read(config_path, encoding='utf-8')
            
            api_key = None
            if config.has_section('DEEPSEEK') and config.has_option('DEEPSEEK', 'API_KEY'):
                api_key = config.get('DEEPSEEK', 'API_KEY').strip()
            
            if api_key and api_key != 'sk-':
                # 有API密钥，显示后四位
                masked_key = f"sk-****...{api_key[-4:]}" if len(api_key) > 7 else "sk-****"
                self.api_status_label.setText("API状态: 已配置")
                self.api_status_label.setStyleSheet("""
                    BodyLabel {
                        color: #155724;
                        font-size: 14px;
                        font-weight: 500;
                        padding: 8px 12px;
                        background-color: #D4EDDA;
                        border: 1px solid #C3E6CB;
                        border-radius: 6px;
                    }
                """)
                self.api_display_label.setText(f"当前API: {masked_key}")
                self.delete_api_btn.setEnabled(True)
            else:
                # 无API密钥
                self.api_status_label.setText("API状态: 未配置")
                self.api_status_label.setStyleSheet("""
                    BodyLabel {
                        color: #DC3545;
                        font-size: 14px;
                        font-weight: 500;
                        padding: 8px 12px;
                        background-color: #F8D7DA;
                        border: 1px solid #F5C6CB;
                        border-radius: 6px;
                    }
                """)
                self.api_display_label.setText("当前API: 未设置")
                self.delete_api_btn.setEnabled(False)
                
        except Exception as e:
            InfoBar.error(
                title="加载失败",
                content=f"无法加载API配置：{str(e)}",
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def create_default_config(self, config_path):
        """
        创建默认配置文件
        """
        try:
            config = configparser.ConfigParser()
            # 保持选项名大小写
            config.optionxform = str
            
            config.add_section('DEEPSEEK')
            config.set('DEEPSEEK', 'API_KEY', 'sk-')
            
            config.add_section('SETTINGS')
            config.set('SETTINGS', 'AI_TIMEOUT', '90')
            config.set('SETTINGS', 'MAX_RETRIES', '2')
            
            with open(config_path, 'w', encoding='utf-8') as f:
                config.write(f)
                
        except Exception as e:
            InfoBar.error(
                title="创建配置文件失败",
                content=f"无法创建配置文件：{str(e)}",
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def save_api_key(self):
        """
        保存API密钥
        """
        try:
            api_key = self.api_input.text().strip()
            
            if not api_key:
                InfoBar.warning(
                    title="输入错误",
                    content="请输入API密钥",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                return
            
            # 验证API密钥格式
            if not api_key.startswith('sk-') or len(api_key) < 10:
                InfoBar.warning(
                    title="格式错误",
                    content="API密钥格式不正确，应以sk-开头且长度足够",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                return
            
            config_path = self.get_config_path()
            
            # 读取现有配置
            config = configparser.ConfigParser()
            # 保持选项名大小写
            config.optionxform = str
            if os.path.exists(config_path):
                try:
                    config.read(config_path, encoding='utf-8')
                except configparser.Error:
                    # 如果配置文件格式错误，删除并重新创建
                    os.remove(config_path)
                    self.create_default_config(config_path)
                    config.read(config_path, encoding='utf-8')
            
            # 确保DEEPSEEK节存在
            if not config.has_section('DEEPSEEK'):
                config.add_section('DEEPSEEK')
            
            # 更新API密钥
            config.set('DEEPSEEK', 'API_KEY', api_key)
            
            # 保存配置
            with open(config_path, 'w', encoding='utf-8') as f:
                config.write(f)
            
            InfoBar.success(
                title="保存成功",
                content="API密钥保存成功！",
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
            
            # 清空输入框
            self.api_input.clear()
            
            # 刷新状态显示
            self.load_api_status()
            
        except Exception as e:
            InfoBar.error(
                title="保存失败",
                content=f"保存API密钥失败：{str(e)}",
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def delete_api_key(self):
        """
        删除API密钥
        """
        try:
            # 确认删除
            reply = MessageBox(
                "确认删除",
                "确定要删除当前的API密钥吗？\\n删除后将无法使用AI分析功能。",
                self
            )
            reply.yesButton.setText("确定")
            reply.cancelButton.setText("取消")
            
            if reply.exec():
                config_path = self.get_config_path()
                
                # 读取现有配置
                config = configparser.ConfigParser()
                # 保持选项名大小写
                config.optionxform = str
                if os.path.exists(config_path):
                    try:
                        config.read(config_path, encoding='utf-8')
                    except configparser.Error:
                        # 如果配置文件格式错误，删除并重新创建
                        os.remove(config_path)
                        self.create_default_config(config_path)
                        config.read(config_path, encoding='utf-8')
                
                # 确保DEEPSEEK节存在
                if not config.has_section('DEEPSEEK'):
                    config.add_section('DEEPSEEK')
                
                # 删除API密钥（设为默认值）
                config.set('DEEPSEEK', 'API_KEY', 'sk-')
                
                # 保存配置
                with open(config_path, 'w', encoding='utf-8') as f:
                    config.write(f)
                
                InfoBar.success(
                    title="删除成功",
                    content="API密钥已删除",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                
                # 刷新状态显示
                self.load_api_status()
                
        except Exception as e:
            InfoBar.error(
                title="删除失败",
                content=f"删除API密钥失败：{str(e)}",
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def test_api_connection(self):
        """
        测试API连接
        """
        try:
            config_path = self.get_config_path()
            
            if not os.path.exists(config_path):
                InfoBar.warning(
                    title="测试失败",
                    content="配置文件不存在",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                return
            
            config = configparser.ConfigParser()
            # 保持选项名大小写
            config.optionxform = str
            try:
                config.read(config_path, encoding='utf-8')
            except configparser.Error:
                # 如果配置文件格式错误，重新创建
                self.create_default_config(config_path)
                InfoBar.warning(
                    title="配置错误",
                    content="配置文件格式错误已修复，请重新配置API密钥",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                return
            
            api_key = None
            if config.has_section('DEEPSEEK') and config.has_option('DEEPSEEK', 'API_KEY'):
                api_key = config.get('DEEPSEEK', 'API_KEY').strip()
            
            if not api_key or api_key == 'sk-':
                InfoBar.warning(
                    title="测试失败",
                    content="请先配置API密钥",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                return
            
            # 显示测试中状态
            InfoBar.info(
                title="测试中",
                content="正在测试API连接，请稍候...",
                duration=2000,
                position=InfoBarPosition.TOP,
                parent=self
            )
            
            # 使用ConnectionTestWorker进行实际的API测试
            self.test_thread = QThread()
            self.test_worker = ConnectionTestWorker()
            self.test_worker.moveToThread(self.test_thread)
            
            # 连接信号
            self.test_thread.started.connect(self.test_worker.run_test)
            self.test_worker.finished.connect(self.on_test_finished)
            self.test_worker.finished.connect(self.test_thread.quit)
            self.test_worker.finished.connect(self.test_worker.deleteLater)
            self.test_thread.finished.connect(self.test_thread.deleteLater)
            
            # 开始测试
            self.test_thread.start()
            
        except Exception as e:
            InfoBar.error(
                title="测试失败",
                content=f"API连接测试失败：{str(e)}",
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def on_test_finished(self, success, message):
        """
        处理API测试结果
        
        Args:
            success (bool): 测试是否成功
            message (str): 测试结果消息
        """
        if success:
            InfoBar.success(
                title="测试成功",
                content=f"API连接正常！{message}",
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
        else:
            InfoBar.error(
                title="测试失败",
                content=f"API连接测试失败：{message}",
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            ) 