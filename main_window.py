#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美莲花美食支出记录系统 - 主窗口
基于 NavigationInterface 的现代化应用程序主框架
使用 PyQt-Fluent-Widgets 实现现代化的 Fluent Design 界面
"""

import sys
from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, 
                             QHBoxLayout, QDialog)
from qfluentwidgets import (FluentWindow, NavigationInterface, NavigationItemPosition, 
                            FluentIcon, TitleLabel, BodyLabel, CardWidget)

# 导入所有功能页面
from query_page import QueryPage
from reporting_page import ReportingPage
from daily_records_page import DailyRecordsPage
from settings_page import SettingsPage


class PlaceholderPage(QWidget):
    """
    占位符页面类 - 用于临时显示页面内容
    """
    
    def __init__(self, title_cn, title_ug, description=""):
        """
        初始化占位符页面
        
        Args:
            title_cn (str): 中文标题
            title_ug (str): 维语标题
            description (str): 页面描述
        """
        super().__init__()
        self.title_cn = title_cn
        self.title_ug = title_ug
        self.description = description
        self.init_ui()
    
    def init_ui(self):
        """
        初始化占位符页面UI
        """
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # 创建卡片容器
        card = CardWidget()
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(15)
        card_layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题
        title = TitleLabel(f"{self.title_cn}\n{self.title_ug}")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 描述
        if self.description:
            desc = BodyLabel(self.description)
            desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
            desc.setWordWrap(True)
        
        # 状态提示
        status = BodyLabel("页面正在开发中...\nبۇ بەت تەرەققىي قىلىنىۋاتىدۇ...")
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        card_layout.addStretch(1)
        card_layout.addWidget(title)
        if self.description:
            card_layout.addWidget(desc)
        card_layout.addWidget(status)
        card_layout.addStretch(1)
        
        layout.addWidget(card)


class ExpenseInputPage(QWidget):
    """
    支出录入页面 - 直接在页面上完成支出录入
    """
    
    def __init__(self, username, user_role, sound_manager=None):
        """
        初始化支出录入页面
        
        Args:
            username (str): 用户名
            user_role (str): 用户角色
            sound_manager: 声音管理器实例
        """
        super().__init__()
        self.username = username
        self.user_role = user_role
        self.sound_manager = sound_manager
        self.selected_category_id = None
        self.category_buttons = []
        self.init_ui()
        self.load_categories()
    
    def init_ui(self):
        """
        初始化用户界面 - 使用左右分布的布局设计
        """
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 10, 15, 10)
        
        # 创建头部标题区域（紧凑版）
        self.create_title_area(main_layout)
        
        # 创建水平分割的内容区域
        self.create_horizontal_content_area(main_layout)
    
    def create_title_area(self, parent_layout):
        """
        创建紧凑的标题区域
        """
        title_card = CardWidget()
        title_layout = QHBoxLayout(title_card)
        title_layout.setContentsMargins(20, 10, 20, 10)
        title_layout.setSpacing(15)
        
        # 主标题（使用SubtitleLabel而不是TitleLabel）
        from qfluentwidgets import SubtitleLabel
        main_title = SubtitleLabel("支出录入 / چىقىم كىرگۈزۈش")
        
        title_layout.addWidget(main_title)
        title_layout.addStretch()
        
        parent_layout.addWidget(title_card)
    
    def create_horizontal_content_area(self, parent_layout):
        """
        创建左右分布的内容区域
        """
        from PyQt6.QtWidgets import QSplitter
        
        # 创建水平分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：分类选择区域
        self.create_left_category_panel(splitter)
        
        # 右侧：输入区域
        self.create_right_input_panel(splitter)
        
        # 设置分割比例 (45% : 55%)
        splitter.setSizes([500, 500])
        splitter.setChildrenCollapsible(False)
        
        parent_layout.addWidget(splitter, 1)
    
    def create_left_category_panel(self, parent_splitter):
        """
        创建左侧分类选择面板
        """
        category_card = CardWidget()
        category_layout = QVBoxLayout(category_card)
        category_layout.setContentsMargins(25, 20, 25, 20)
        category_layout.setSpacing(15)
        
        # 标题
        from qfluentwidgets import SubtitleLabel
        category_title = SubtitleLabel("选择支出类型 / چىقىم تۈرىنى تاللاڭ")
        category_layout.addWidget(category_title)
        
        # 滚动区域
        from qfluentwidgets import ScrollArea
        from PyQt6.QtWidgets import QGridLayout
        
        self.category_scroll = ScrollArea()
        self.category_scroll.setMinimumHeight(400)
        self.category_scroll.setWidgetResizable(True)
        self.category_scroll.setStyleSheet("ScrollArea { background-color: #D6EFD8; border: none; }")
        
        self.category_widget = QWidget()
        self.category_widget.setStyleSheet("QWidget { background-color: #D6EFD8; }")
        self.category_grid_layout = QGridLayout(self.category_widget)
        self.category_grid_layout.setSpacing(8)
        self.category_scroll.setWidget(self.category_widget)
        
        category_layout.addWidget(self.category_scroll)
        parent_splitter.addWidget(category_card)
    
    def create_right_input_panel(self, parent_splitter):
        """
        创建右侧输入面板 
        """
        input_card = CardWidget()
        input_layout = QVBoxLayout(input_card)
        input_layout.setContentsMargins(25, 20, 25, 20)
        input_layout.setSpacing(15)
        
        # 标题
        from qfluentwidgets import SubtitleLabel
        input_title = SubtitleLabel("输入日期、金额和备注 / چېسلا، پۇل مىقدارى ۋە ئىزاھات كىرگۈزۈڭ")
        input_layout.addWidget(input_title)
        
        # 添加一些垂直空间
        input_layout.addSpacing(20)
        
        # 日期选择区域
        self.create_date_input_section(input_layout)
        
        # 金额输入区域
        self.create_amount_input_section(input_layout)
        
        # 备注输入区域
        self.create_notes_input_section(input_layout)
        
        # 保存按钮区域
        self.create_save_button_section(input_layout)
        
        # 添加伸缩空间
        input_layout.addStretch()
        
        parent_splitter.addWidget(input_card)
    
    def create_date_input_section(self, parent_layout):
        """
        创建日期选择区域
        """
        date_layout = QVBoxLayout()
        date_layout.setSpacing(10)
        
        date_label = BodyLabel("支出日期 / چىقىم چېسلاسى:")
        date_label.setStyleSheet("font-weight: bold; color: black;")
        
        from qfluentwidgets import DateEdit
        from PyQt6.QtCore import QDate
        self.date_input = DateEdit()
        self.date_input.setDate(QDate.currentDate())  # 默认今天
        self.date_input.setCalendarPopup(True)
        self.date_input.setMinimumHeight(35)
        self.date_input.setMinimumWidth(250)
        self.date_input.setMaximumWidth(300)
        
        # 设置日期格式显示
        self.date_input.setDisplayFormat("yyyy-MM-dd")  # 显示完整日期格式
        
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_input)
        
        parent_layout.addLayout(date_layout)
        parent_layout.addSpacing(15)
    
    def create_amount_input_section(self, parent_layout):
        """
        创建金额输入区域 
        """
        amount_layout = QVBoxLayout()
        amount_layout.setSpacing(10)
        
        amount_label = BodyLabel("金额 / پۇل مىقدارى:")
        amount_label.setStyleSheet("font-weight: bold; color: black;")
        
        from qfluentwidgets import LineEdit
        self.amount_input = LineEdit()
        self.amount_input.setPlaceholderText("请输入金额 / پۇل مىقدارىنى كىرگۈزۈڭ")
        self.amount_input.setMinimumHeight(35)
        
        # 设置数字验证器
        from PyQt6.QtGui import QDoubleValidator
        validator = QDoubleValidator(0.00, 999999.99, 2)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.amount_input.setValidator(validator)
        
        amount_layout.addWidget(amount_label)
        amount_layout.addWidget(self.amount_input)
        
        parent_layout.addLayout(amount_layout)
        parent_layout.addSpacing(15)
        
        # 连接输入框变化事件
        self.amount_input.textChanged.connect(self.check_input_validity)
    
    def create_notes_input_section(self, parent_layout):
        """
        创建备注输入区域
        """
        notes_layout = QVBoxLayout()
        notes_layout.setSpacing(10)
        
        notes_label = BodyLabel("备注 / ئىزاھات:")
        notes_label.setStyleSheet("font-weight: bold; color: black;")
        
        from qfluentwidgets import LineEdit
        self.notes_input = LineEdit()
        self.notes_input.setPlaceholderText("备注信息（可选）/ ئىزاھات ئۇچۇرى（تاللاشچان）")
        self.notes_input.setMinimumHeight(35)
        
        notes_layout.addWidget(notes_label)
        notes_layout.addWidget(self.notes_input)
        
        parent_layout.addLayout(notes_layout)
        parent_layout.addSpacing(25)
    
    def create_save_button_section(self, parent_layout):
        """
        创建保存按钮区域
        """
        button_layout = QHBoxLayout()
        from qfluentwidgets import PrimaryPushButton
        
        self.save_btn = PrimaryPushButton("保存支出记录 / چىقىم خاتىرىسىنى ساقلاش")
        self.save_btn.setMinimumHeight(40)
        self.save_btn.setMinimumWidth(200)
        self.save_btn.setEnabled(False)  # 初始禁用
        self.save_btn.clicked.connect(self.save_expense)
        
        # 连接保存按钮音效
        if self.sound_manager:
            self.save_btn.clicked.connect(self.sound_manager.play_confirmation)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addStretch()
        
        parent_layout.addLayout(button_layout)
    
    def load_categories(self):
        """
        加载支出分类
        """
        try:
            from models import get_all_categories
            categories = get_all_categories()
            
            if not categories:
                from qfluentwidgets import InfoBar, InfoBarPosition
                InfoBar.info(
                    title="提示 / ئەسكەرتىش",
                    content="暂无支出分类，请先在设置中添加\nھازىر چىقىم تۈرى يوق، ئالدى بىلەن تەڭشەكتە قوشۇڭ",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                return
            
            # 清空现有按钮
            for button in self.category_buttons:
                button.setParent(None)
            self.category_buttons.clear()
            
            # 创建分类按钮（每行3个）
            row = 0
            col = 0
            max_cols = 3
            
            for category in categories:
                from qfluentwidgets import PushButton
                
                button = PushButton()
                # 显示表情图标、中文名称和维语名称
                emoji = category.get('emoji', '📝')
                button.setText(f"{emoji}\n{category['name_cn']}\n{category['name_ug']}")
                button.setMinimumHeight(80)
                button.setMinimumWidth(160)
                button.setMaximumWidth(200)
                # 设置默认样式
                button.setStyleSheet("""
                    PushButton {
                        background-color: white;
                        border: 1px solid #508D4E;
                        color: #1A5319;
                        border-radius: 8px;
                        font-weight: normal;
                        font-size: 12px;
                        text-align: center;
                        padding: 8px;
                    }
                    PushButton:hover {
                        background-color: #F0F8F0;
                        border: 2px solid #508D4E;
                    }
                """)
                
                # 存储分类ID和相关信息
                button.category_id = category['id']
                button.category_name_cn = category['name_cn']
                button.category_name_ug = category['name_ug']
                button.category_emoji = emoji
                
                # 连接点击事件
                button.clicked.connect(lambda checked, btn=button: self.select_category(btn))
                
                # 连接分类按钮音效
                if self.sound_manager:
                    button.clicked.connect(self.sound_manager.play_click)
                
                # 添加到布局
                self.category_grid_layout.addWidget(button, row, col)
                self.category_buttons.append(button)
            
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            
        except Exception as e:
            from qfluentwidgets import InfoBar, InfoBarPosition
            InfoBar.error(
                title="加载失败 / يۈكلەش مەغلۇب بولدى",
                content=f"无法加载支出分类：{str(e)}\nچىقىم تۈرىنى يۈكلىيەلمىدى: {str(e)}",
                duration=4000,
                position=InfoBarPosition.TOP,
                parent=self
            )

    def select_category(self, selected_button):
        """
        选择支出分类
        """
        # 重置所有按钮样式
        for button in self.category_buttons:
            button.setStyleSheet("""
                PushButton {
                    background-color: white;
                    border: 1px solid #508D4E;
                    color: #1A5319;
                    border-radius: 8px;
                    font-weight: normal;
                    font-size: 12px;
                    text-align: center;
                    padding: 8px;
                }
                PushButton:hover {
                    background-color: #F0F8F0;
                    border: 2px solid #508D4E;
                }
            """)
        
        # 设置选中按钮的样式
        selected_button.setStyleSheet("""
            PushButton {
                background-color: #1A5319;
                border: 2px solid #508D4E;
                color: white;
                font-weight: bold;
                font-size: 12px;
                text-align: center;
                padding: 8px;
                border-radius: 8px;
            }
            PushButton:hover {
                background-color: #508D4E;
            }
        """)
            
        # 保存选中的分类
        self.selected_category_id = selected_button.category_id
            
        # 检查输入有效性
        self.check_input_validity()
    
    def check_input_validity(self):
        """
        检查输入是否有效，控制保存按钮状态
        """
        amount_valid = bool(self.amount_input.text().strip() and float(self.amount_input.text() or 0) > 0)
        category_selected = self.selected_category_id is not None
        
        self.save_btn.setEnabled(amount_valid and category_selected)
    
    def save_expense(self):
        """
        保存支出记录
        """
        try:
            from models import add_expense, get_user_id_by_username
            
            # 获取输入数据
            amount = float(self.amount_input.text())
            notes = self.notes_input.text().strip()
            expense_date = self.date_input.date().toString("yyyy-MM-dd")  # 使用用户选择的日期
            
            # 获取用户ID
            user_id = get_user_id_by_username(self.username)
            if user_id is None:
                user_id = 1  # 默认用户ID
            
            # 保存支出记录
            success = add_expense(expense_date, amount, self.selected_category_id, user_id, notes)
            
            if success:
                from qfluentwidgets import InfoBar, InfoBarPosition
                InfoBar.success(
                    title="保存成功 / ساقلاش مۇۋەپپەقىيەتلىك",
                    content=f"支出记录已保存：¥{amount:.2f}\nچىقىم خاتىرىسى ساقلاندى: ¥{amount:.2f}",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                
                # 清空输入
                self.amount_input.clear()
                self.notes_input.clear()
                
                # 重置分类选择
                for button in self.category_buttons:
                    button.setStyleSheet("""
                        PushButton {
                            background-color: white;
                            border: 1px solid #508D4E;
                            color: #1A5319;
                            border-radius: 8px;
                            font-weight: normal;
                            font-size: 12px;
                            text-align: center;
                            padding: 8px;
                        }
                        PushButton:hover {
                            background-color: #F0F8F0;
                            border: 2px solid #508D4E;
                        }
                    """)
                self.selected_category_id = None
                
                # 禁用保存按钮
                self.save_btn.setEnabled(False)
            else:
                from qfluentwidgets import InfoBar, InfoBarPosition
                InfoBar.error(
                    title="保存失败 / ساقلاش مەغلۇب بولدى",
                    content="支出记录保存失败\nچىقىم خاتىرىسى ساقلاش مەغلۇب بولدى",
                    duration=4000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                
        except Exception as e:
            from qfluentwidgets import InfoBar, InfoBarPosition
            InfoBar.error(
                title="保存失败 / ساقلاش مەغلۇب بولدى",
                content=f"保存时发生错误：{str(e)}\nساقلاشتا خاتالىق كۆرۈلدى: {str(e)}",
                duration=4000,
                position=InfoBarPosition.TOP,
                parent=self
            )


class MainWindow(FluentWindow):
    """
    主窗口类 - 基于 NavigationInterface 的现代化应用程序主框架
    提供统一的导航界面和页面管理功能
    """
    
    def __init__(self, username, user_role, sound_manager=None):
        """
        初始化主窗口
        
        Args:
            username (str): 登录用户名
            user_role (str): 用户角色
            sound_manager: 声音管理器实例
        """
        super().__init__()
        
        # 开启亚克力特效 - 使用与登录页面相同的设置
        self.windowEffect.setAcrylicEffect(self.winId(), "F2F2F230")
        
        self.username = username
        self.user_role = user_role
        self.sound_manager = sound_manager
        
        # 在初始化阶段暂时禁用音效，避免初始化触发多个音效
        if self.sound_manager:
            self.sound_manager.disable_sounds()
        
        # 初始化UI
        self.init_ui()
        self.init_navigation()
        
        # 初始化完成后重新启用音效
        if self.sound_manager:
            self.sound_manager.enable_sounds()
        
        # 设置窗口属性和新标题栏的标题
        self.setWindowTitle(f"美莲花美食支出记录系统 - {self.username} ({self.user_role}) / نىلۇپەر تائاملار سارىيى چىقىم خاتىرىسى سىستېمىسى - {self.username} ({self.user_role})")
        self.titleBar.setTitle("美莲花美食支出记录系统 / نىلۇپەر تائاملار سارىيى چىقىم خاتىرىسى سىستېمىسى")
        
        # 设置窗口为全屏显示
        self.setMinimumSize(1200, 700)
        self.showMaximized()  # 直接设置为最大化（全屏）
        
        # --- 开始应用自定义品牌主题QSS ---
        custom_qss = """
            /* 将窗口主背景设置为透明，让亚克力效果显示 */
            FluentWindow {
                background: transparent;
            }

            /* 强制导航界面和标题栏透明 */
            NavigationInterface, NavigationPanel, TitleBar, FluentTitleBar {
                background: transparent !important;
                background-color: transparent !important;
                border: none;
            }

            /* 确保内容区的页面保持浅绿色背景 */
            StackedWidget > QWidget {
               background: #D6EFD8;
            }

            /* 设置导航项的颜色和透明背景 */
            NavigationPushButton, NavigationToolButton {
                border-radius: 7px;
                color: #1A5319;
                background: rgba(255, 255, 255, 0.1);
            }
            NavigationPushButton:hover, NavigationToolButton:hover {
                background: rgba(80, 141, 78, 0.8);
                color: white;
            }
            NavigationPushButton:checked, NavigationToolButton:checked {
                background: rgba(26, 83, 25, 0.9);
                color: white;
            }

            /* 确保顶部控件透明 */
            NavigationDisplayModeButton, NavigationAvatarWidget {
                background: transparent;
            }
        """
        self.setStyleSheet(custom_qss)
        # --- 自定义品牌主题QSS应用结束 ---
    
    def init_ui(self):
        """
        初始化用户界面
        """
        # FluentWindow 已经内置了 NavigationInterface，无需手动创建
        # 设置导航界面属性
        self.navigationInterface.setExpandWidth(300)

    def init_navigation(self):
        """
        初始化导航菜单
        """
        # 创建页面实例
        self.expense_input_page = ExpenseInputPage(self.username, self.user_role, self.sound_manager)
        
        # 创建所有功能页面实例
        self.query_page = QueryPage(self.sound_manager)
        self.report_page = ReportingPage(self.sound_manager, self.username)
        self.daily_management_page = DailyRecordsPage(self.sound_manager)
        
        # 获取用户ID用于设置页面
        from models import get_user_id_by_username
        user_id = get_user_id_by_username(self.username)
        if user_id is None:
            user_id = 1  # 默认用户ID
        self.settings_page = SettingsPage(user_id, self.username, self.sound_manager)
            
        # 连接页面间的信号
        # 设置页面的分类更新信号连接到支出录入页面的分类刷新
        self.settings_page.categories_updated.connect(self.expense_input_page.load_categories)
        
        # 设置页面对象名称（FluentWindow 要求）
        self.expense_input_page.setObjectName("expense_input")
        self.query_page.setObjectName("query")
        self.report_page.setObjectName("report")
        self.daily_management_page.setObjectName("daily")
        self.settings_page.setObjectName("settings")
        
        # 添加主要导航项
        self.addSubInterface(
            self.expense_input_page,
            FluentIcon.HOME,
            "支出录入 / چىقىم كىرگۈزۈش"
        )
        
        self.addSubInterface(
            self.daily_management_page,
            FluentIcon.EDIT,
            "每日管理 / كۈنلۈك خاتىرە باشقۇرۇش"
        )
        
        self.addSubInterface(
            self.query_page,
            FluentIcon.SEARCH,
            "查询记录 / خاتىرە كۆرۈش"
        )
        
        self.addSubInterface(
            self.report_page,
            FluentIcon.PIE_SINGLE,
            "报表中心 / دوكلات مەركىزى"
        )
        
        # 添加设置页面到主导航项（仅管理员可见）
        if self.username == "admin":
            self.addSubInterface(
                self.settings_page,
                FluentIcon.SETTING,
                "系统设置 / سىستېما تەڭشىكى"
            )
        
        # 设置默认选中项
        self.navigationInterface.setCurrentItem("expense_input")
        
        # --- 为导航项添加点击音效 ---
        # 通过重写 switchTo 方法来实现导航音效
        self._setup_navigation_sounds()
    
    def _setup_navigation_sounds(self):
        """
        设置导航音效 - 通过重写 switchTo 方法实现
        """
        if not self.sound_manager:
            return
            
        # 保存原始的 switchTo 方法
        self._original_switchTo = self.switchTo
        
        # 重写 switchTo 方法，在切换页面前播放音效
        def switchTo_with_sound(interface):
            # 播放点击音效
            self.sound_manager.play_click()
            # 调用原始的 switchTo 方法
            self._original_switchTo(interface)
        
        # 替换 switchTo 方法
        self.switchTo = switchTo_with_sound
        
        # 为展开/收缩按钮添加音效
        self._setup_menu_button_sound()
    
    def _setup_menu_button_sound(self):
        """
        为导航栏的展开/收缩按钮添加音效
        """
        if not self.sound_manager:
            return
            
        try:
            # 获取导航面板的菜单按钮
            menu_button = self.navigationInterface.panel.menuButton
            if menu_button:
                # 连接菜单按钮的点击信号到音效
                menu_button.clicked.connect(self.sound_manager.play_click)
        except (AttributeError, TypeError):
            # 如果无法访问菜单按钮，静默处理
            pass
