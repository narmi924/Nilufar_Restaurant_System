#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美莲花美食支出记录系统 - 设置窗口
使用 PyQt-Fluent-Widgets 实现现代化的 Fluent Design 界面
"""

import sys
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QApplication, QMessageBox)
from qfluentwidgets import (FluentWindow, TitleLabel, SubtitleLabel, BodyLabel, 
                            LineEdit, PasswordLineEdit, PrimaryPushButton, PushButton, 
                            ScrollArea, CardWidget, InfoBar, InfoBarPosition,
                            MessageBox, SegmentedWidget)

from models import (update_user_credentials, get_all_users, add_user, delete_user, 
                    get_all_categories, add_category, delete_category)


class SettingsWindow(FluentWindow):
    """
    设置窗口类 - 使用 Fluent Design 风格
    提供用户管理和分类管理功能，具有现代化的选项卡界面
    """
    
    # 定义信号，当分类更新时发出
    categories_updated = pyqtSignal()
    
    def __init__(self, user_id, username, parent=None):
        """
        初始化设置窗口
        
        Args:
            user_id (int): 当前用户ID
            username (str): 当前用户名
            parent: 父窗口
        """
        super().__init__(parent)
        self.user_id = user_id
        self.username = username
        self.category_inputs = []  # 存储分类输入框
        
        self.init_ui()
        self.load_users()
        self.load_categories()
    
    def init_ui(self):
        """
        初始化用户界面
        """
        # 设置窗口标题
        self.setWindowTitle("系统设置 / سىستېما تەڭشىكى")
        
        # 设置窗口大小为全屏
        self.setWindowState(Qt.WindowState.WindowMaximized)
        
        # 创建主容器
        main_widget = QWidget()
        main_widget.setObjectName("settings_interface")  # 设置对象名称
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 20, 30, 20)
        
        # 创建标题
        title_label = TitleLabel("系统设置 / سىستېما تەڭشىكى")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 创建选项卡容器
        from PyQt6.QtWidgets import QStackedWidget
        self.stacked_widget = QStackedWidget()
        
        # 创建选项卡切换器
        self.tab_selector = SegmentedWidget()
        self.tab_selector.addItem("user_management", "用户管理 / ئىشلەتكۈچى باشقۇرۇش")
        self.tab_selector.addItem("category_management", "分类管理 / تۈر باشقۇرۇش")
        self.tab_selector.setFixedHeight(40)
        self.tab_selector.currentItemChanged.connect(self.on_tab_changed)
        
        main_layout.addWidget(self.tab_selector, 0, Qt.AlignmentFlag.AlignCenter)
        
        # 创建用户管理选项卡
        self.create_user_management_tab()
        
        # 创建分类管理选项卡
        self.create_category_management_tab()
        
        main_layout.addWidget(self.stacked_widget)
        
        # 设置默认选中
        self.tab_selector.setCurrentItem("user_management")
        self.stacked_widget.setCurrentIndex(0)
        
        # 创建底部关闭按钮
        self.create_bottom_buttons(main_layout)
        
        # 使用addSubInterface方法添加界面
        self.addSubInterface(main_widget, "settings_interface", "设置")
    
    def create_user_management_tab(self):
        """
        创建用户管理选项卡
        """
        user_tab = QWidget()
        user_layout = QVBoxLayout(user_tab)
        user_layout.setSpacing(20)
        user_layout.setContentsMargins(20, 20, 20, 20)
        
        # 修改密码区域
        password_card = CardWidget()
        password_layout = QVBoxLayout(password_card)
        password_layout.setSpacing(15)
        password_layout.setContentsMargins(20, 20, 20, 20)
        
        password_title = SubtitleLabel("修改密码 / مەخپىي نومۇر ئۆزگەرتىش")
        password_layout.addWidget(password_title)
        
        # 当前密码
        current_password_layout = QHBoxLayout()
        current_password_label = BodyLabel("当前密码 / ھازىرقى مەخپىي نومۇر:")
        current_password_label.setMinimumWidth(150)
        self.current_password_input = PasswordLineEdit()
        self.current_password_input.setPlaceholderText("请输入当前密码 / ھازىرقى مەخپىي نومۇرنى كىرگۈزۈڭ")
        current_password_layout.addWidget(current_password_label)
        current_password_layout.addWidget(self.current_password_input)
        password_layout.addLayout(current_password_layout)
        
        # 新密码
        new_password_layout = QHBoxLayout()
        new_password_label = BodyLabel("新密码 / يېڭى مەخپىي نومۇر:")
        new_password_label.setMinimumWidth(150)
        self.new_password_input = PasswordLineEdit()
        self.new_password_input.setPlaceholderText("请输入新密码 / يېڭى مەخپىي نومۇرنى كىرگۈزۈڭ")
        new_password_layout.addWidget(new_password_label)
        new_password_layout.addWidget(self.new_password_input)
        password_layout.addLayout(new_password_layout)
        
        # 确认密码
        confirm_password_layout = QHBoxLayout()
        confirm_password_label = BodyLabel("确认密码 / مەخپىي نومۇرنى جەزملەش:")
        confirm_password_label.setMinimumWidth(150)
        self.confirm_password_input = PasswordLineEdit()
        self.confirm_password_input.setPlaceholderText("请再次输入新密码 / يېڭى مەخپىي نومۇرنى قايتا كىرگۈزۈڭ")
        confirm_password_layout.addWidget(confirm_password_label)
        confirm_password_layout.addWidget(self.confirm_password_input)
        password_layout.addLayout(confirm_password_layout)
        
        # 修改密码按钮
        change_password_btn = PrimaryPushButton("修改密码 / مەخپىي نومۇر ئۆزگەرتىش")
        change_password_btn.setMinimumHeight(40)
        change_password_btn.clicked.connect(self.change_password)
        password_layout.addWidget(change_password_btn)
        
        user_layout.addWidget(password_card)
        
        # 用户管理区域（仅管理员可见）
        if self.username == "admin":
            user_mgmt_card = CardWidget()
            user_mgmt_layout = QVBoxLayout(user_mgmt_card)
            user_mgmt_layout.setSpacing(15)
            user_mgmt_layout.setContentsMargins(20, 20, 20, 20)
            
            user_mgmt_title = SubtitleLabel("用户管理 / ئىشلەتكۈچى باشقۇرۇش")
            user_mgmt_layout.addWidget(user_mgmt_title)
            
            # 添加用户区域
            add_user_layout = QHBoxLayout()
            username_label = BodyLabel("用户名 / ئىشلەتكۈچى نامى:")
            username_label.setMinimumWidth(120)
            self.new_username_input = LineEdit()
            self.new_username_input.setPlaceholderText("输入新用户名 / يېڭى ئىشلەتكۈچى نامىنى كىرگۈزۈڭ")
            
            password_label = BodyLabel("密码 / مەخپىي نومۇر:")
            password_label.setMinimumWidth(120)
            self.new_user_password_input = PasswordLineEdit()
            self.new_user_password_input.setPlaceholderText("输入密码 / مەخپىي نومۇرنى كىرگۈزۈڭ")
            
            add_user_btn = PushButton("添加用户 / ئىشلەتكۈچى قوشۇش")
            add_user_btn.clicked.connect(self.add_user)
            
            add_user_layout.addWidget(username_label)
            add_user_layout.addWidget(self.new_username_input)
            add_user_layout.addWidget(password_label)
            add_user_layout.addWidget(self.new_user_password_input)
            add_user_layout.addWidget(add_user_btn)
            user_mgmt_layout.addLayout(add_user_layout)
            
            # 用户列表滚动区域
            self.users_scroll = ScrollArea()
            self.users_scroll.setMinimumHeight(200)
            self.users_scroll.setWidgetResizable(True)
            
            self.users_widget = QWidget()
            self.users_layout = QVBoxLayout(self.users_widget)
            self.users_layout.setSpacing(10)
            self.users_scroll.setWidget(self.users_widget)
            
            user_mgmt_layout.addWidget(self.users_scroll)
            user_layout.addWidget(user_mgmt_card)
        
        user_layout.addStretch()
        self.stacked_widget.addWidget(user_tab)
    
    def create_category_management_tab(self):
        """
        创建分类管理选项卡
        """
        category_tab = QWidget()
        category_layout = QVBoxLayout(category_tab)
        category_layout.setSpacing(20)
        category_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        category_title = SubtitleLabel("分类管理 / تۈر باشقۇرۇش")
        category_layout.addWidget(category_title)
        
        # 添加分类区域
        add_category_card = CardWidget()
        add_category_layout = QVBoxLayout(add_category_card)
        add_category_layout.setSpacing(15)
        add_category_layout.setContentsMargins(20, 20, 20, 20)
        
        add_category_title = BodyLabel("添加新分类 / يېڭى تۈر قوشۇش")
        add_category_layout.addWidget(add_category_title)
        
        # 中文名称输入
        cn_name_layout = QHBoxLayout()
        cn_name_label = BodyLabel("中文名称:")
        cn_name_label.setMinimumWidth(100)
        self.cn_name_input = LineEdit()
        self.cn_name_input.setPlaceholderText("输入中文分类名称")
        cn_name_layout.addWidget(cn_name_label)
        cn_name_layout.addWidget(self.cn_name_input)
        add_category_layout.addLayout(cn_name_layout)
        
        # 维语名称输入
        ug_name_layout = QHBoxLayout()
        ug_name_label = BodyLabel("维语名称:")
        ug_name_label.setMinimumWidth(100)
        self.ug_name_input = LineEdit()
        self.ug_name_input.setPlaceholderText("ئۇيغۇرچە تۈر نامىنى كىرگۈزۈڭ")
        ug_name_layout.addWidget(ug_name_label)
        ug_name_layout.addWidget(self.ug_name_input)
        add_category_layout.addLayout(ug_name_layout)
        
        # 添加按钮
        add_category_btn = PrimaryPushButton("添加分类 / تۈر قوشۇش")
        add_category_btn.setMinimumHeight(40)
        add_category_btn.clicked.connect(self.add_category)
        add_category_layout.addWidget(add_category_btn)
        
        category_layout.addWidget(add_category_card)
        
        # 现有分类列表
        categories_card = CardWidget()
        categories_layout = QVBoxLayout(categories_card)
        categories_layout.setSpacing(15)
        categories_layout.setContentsMargins(20, 20, 20, 20)
        
        categories_title = BodyLabel("现有分类 / مەۋجۇت تۈرلەر")
        categories_layout.addWidget(categories_title)
        
        self.categories_scroll = ScrollArea()
        self.categories_scroll.setMinimumHeight(300)
        self.categories_scroll.setWidgetResizable(True)
        
        self.categories_widget = QWidget()
        self.categories_layout = QVBoxLayout(self.categories_widget)
        self.categories_layout.setSpacing(10)
        self.categories_scroll.setWidget(self.categories_widget)
        
        categories_layout.addWidget(self.categories_scroll)
        category_layout.addWidget(categories_card)
        
        category_layout.addStretch()
        self.stacked_widget.addWidget(category_tab)
    
    def on_tab_changed(self, key):
        """
        处理选项卡切换
        
        Args:
            key (str): 选项卡键值
        """
        index = 0 if key == "user_management" else 1
        self.stacked_widget.setCurrentIndex(index)
    
    def create_bottom_buttons(self, parent_layout):
        """
        创建底部按钮区域
        """
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 20, 0, 0)
        
        # 关闭按钮
        close_button = PushButton("关闭 / تاقاش")
        close_button.setMinimumHeight(40)
        close_button.setMinimumWidth(120)
        close_button.clicked.connect(self.close)
        
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        parent_layout.addLayout(button_layout)
    
    def load_users(self):
        """
        加载用户列表
        """
        if self.username != "admin":
            return
            
        try:
            users = get_all_users()
            
            # 清空现有用户显示
            for i in reversed(range(self.users_layout.count())):
                self.users_layout.itemAt(i).widget().setParent(None)
            
            # 添加用户卡片
            for user in users:
                user_card = CardWidget()
                user_layout = QHBoxLayout(user_card)
                user_layout.setContentsMargins(15, 10, 15, 10)
                
                # 用户信息
                user_info = BodyLabel(f"用户: {user['username']} / ئىشلەتكۈچى: {user['username']}")
                user_layout.addWidget(user_info)
                
                # 删除按钮（不能删除admin）
                if user['username'] != 'admin':
                    delete_btn = PushButton("删除 / ئۆچۈرۈش")
                    delete_btn.setMaximumWidth(100)
                    delete_btn.clicked.connect(lambda checked, u=user: self.delete_user(u['id'], u['username']))
                    user_layout.addWidget(delete_btn)
                
                self.users_layout.addWidget(user_card)
                
        except Exception as e:
            InfoBar.error(
                title="加载失败",
                content=f"无法加载用户列表：{str(e)}",
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def load_categories(self):
        """
        加载分类列表
        """
        try:
            categories = get_all_categories()
            
            # 清空现有分类显示
            for i in reversed(range(self.categories_layout.count())):
                self.categories_layout.itemAt(i).widget().setParent(None)
            
            # 添加分类卡片
            for category in categories:
                category_card = CardWidget()
                category_layout = QHBoxLayout(category_card)
                category_layout.setContentsMargins(15, 10, 15, 10)
                
                # 分类信息
                category_info = BodyLabel(f"{category['name_cn']} / {category['name_ug']}")
                category_layout.addWidget(category_info)
                
                # 删除按钮
                delete_btn = PushButton("删除 / ئۆچۈرۈش")
                delete_btn.setMaximumWidth(100)
                delete_btn.clicked.connect(lambda checked, c=category: self.delete_category(c['id'], c['name_cn']))
                category_layout.addWidget(delete_btn)
                
                self.categories_layout.addWidget(category_card)
                
        except Exception as e:
            InfoBar.error(
                title="加载失败",
                content=f"无法加载分类列表：{str(e)}",
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def change_password(self):
        """
        修改密码
        """
        try:
            current_password = self.current_password_input.text()
            new_password = self.new_password_input.text()
            confirm_password = self.confirm_password_input.text()
            
            # 验证输入
            if not current_password or not new_password or not confirm_password:
                InfoBar.warning(
                    title="输入错误",
                    content="请填写所有密码字段 / بارلىق مەخپىي نومۇر بۆلىكىنى تولدۇرۇڭ",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                return
            
            if new_password != confirm_password:
                InfoBar.warning(
                    title="密码不匹配",
                    content="新密码和确认密码不匹配 / يېڭى مەخپىي نومۇر بىلەن جەزملەش مەخپىي نومۇرى ماسلاشمايدۇ",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                return
            
            # 尝试修改密码
            success, message = update_user_credentials(self.user_id, current_password, new_password=new_password)
            if success:
                InfoBar.success(
                    title="修改成功",
                    content="密码修改成功 / مەخپىي نومۇر مۇۋەپپەقىيەتلىك ئۆزگەرتىلدى",
                    duration=2000,
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
                    content=f"密码修改失败: {message}",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                
        except Exception as e:
            InfoBar.error(
                title="修改失败",
                content=f"密码修改失败：{str(e)}\nمەخپىي نومۇر ئۆزگەرتىش مەغلۇب بولدى: {str(e)}",
                duration=4000,
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
            
            if not username or not password:
                InfoBar.warning(
                    title="输入错误",
                    content="请填写用户名和密码 / ئىشلەتكۈچى نامى ۋە مەخپىي نومۇرنى تولدۇرۇڭ",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                return
            
            if add_user(username, password):
                InfoBar.success(
                    title="添加成功",
                    content=f"用户 {username} 添加成功 / ئىشلەتكۈچى {username} مۇۋەپپەقىيەتلىك قوشۇلدى",
                    duration=2000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                
                # 清空输入框并重新加载用户列表
                self.new_username_input.clear()
                self.new_user_password_input.clear()
                self.load_users()
            else:
                InfoBar.error(
                    title="添加失败",
                    content="用户名已存在 / ئىشلەتكۈچى نامى مەۋجۇت",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                
        except Exception as e:
            InfoBar.error(
                title="添加失败",
                content=f"添加用户失败：{str(e)}\nئىشلەتكۈچى قوشۇش مەغلۇب بولدى: {str(e)}",
                duration=4000,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def delete_user(self, user_id, username):
        """
        删除用户
        """
        if self.username != "admin":
            return
            
        try:
            # 确认删除
            dialog = MessageBox(
                "确认删除",
                f"确定要删除用户 {username} 吗？\n{username} ئىشلەتكۈچىسىنى ئۆچۈرۈشنى جەزملەشتۈرەمسىز؟",
                self
            )
            dialog.yesButton.setText("确定")
            dialog.cancelButton.setText("取消")
            if dialog.exec() != dialog.Accepted:
                return
            
            if delete_user(user_id):
                InfoBar.success(
                    title="删除成功",
                    content=f"用户 {username} 删除成功 / ئىشلەتكۈچى {username} مۇۋەپپەقىيەتلىك ئۆچۈرۈلدى",
                    duration=2000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                
                # 重新加载用户列表
                self.load_users()
            else:
                InfoBar.error(
                    title="删除失败",
                    content="无法删除用户 / ئىشلەتكۈچىنى ئۆچۈرەلمىدى",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                
        except Exception as e:
            InfoBar.error(
                title="删除失败",
                content=f"删除用户失败：{str(e)}\nئىشلەتكۈچى ئۆچۈرۈش مەغلۇب بولدى: {str(e)}",
                duration=4000,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def add_category(self):
        """
        添加分类
        """
        try:
            cn_name = self.cn_name_input.text().strip()
            ug_name = self.ug_name_input.text().strip()
            
            if not cn_name or not ug_name:
                InfoBar.warning(
                    title="输入错误",
                    content="请填写中文和维语名称 / خەنزۇچە ۋە ئۇيغۇرچە نامنى تولدۇرۇڭ",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                return
            
            if add_category(cn_name, ug_name):
                InfoBar.success(
                    title="添加成功",
                    content=f"分类 {cn_name} / {ug_name} 添加成功",
                    duration=2000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                
                # 清空输入框并重新加载分类列表
                self.cn_name_input.clear()
                self.ug_name_input.clear()
                self.load_categories()
                
                # 发出分类更新信号
                self.categories_updated.emit()
            else:
                InfoBar.error(
                    title="添加失败",
                    content="分类已存在 / تۈر مەۋجۇت",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                
        except Exception as e:
            InfoBar.error(
                title="添加失败",
                content=f"添加分类失败：{str(e)}\nتۈر قوشۇش مەغلۇب بولدى: {str(e)}",
                duration=4000,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def delete_category(self, category_id, category_name):
        """
        删除分类
        """
        try:
            # 确认删除
            dialog = MessageBox(
                "确认删除",
                f"确定要删除分类 {category_name} 吗？\n{category_name} تۈرىنى ئۆچۈرۈشنى جەزملەشتۈرەمسىز؟",
                self
            )
            dialog.yesButton.setText("确定")
            dialog.cancelButton.setText("取消")
            if dialog.exec() != dialog.Accepted:
                return
            
            if delete_category(category_id):
                InfoBar.success(
                    title="删除成功",
                    content=f"分类 {category_name} 删除成功",
                    duration=2000,
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
                    content="无法删除分类，可能有相关记录 / تۈرنى ئۆچۈرەلمىدى، مۇناسىۋەتلىك خاتىرە بولۇشى مۇمكىن",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                
        except Exception as e:
            InfoBar.error(
                title="删除失败",
                content=f"删除分类失败：{str(e)}\nتۈر ئۆچۈرۈش مەغلۇب بولدى: {str(e)}",
                duration=4000,
                position=InfoBarPosition.TOP,
                parent=self
            )


