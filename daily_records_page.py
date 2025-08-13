#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美莲花美食支出记录系统 - 每日记录页面
基于 Fluent Design 的功能页面，可嵌入到 NavigationInterface 中
"""

import sys
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QHeaderView, QAbstractItemView, QTableWidgetItem, QMainWindow)
from qfluentwidgets import (TitleLabel, SubtitleLabel, BodyLabel, 
                            LineEdit, PrimaryPushButton, PushButton, DateEdit,
                            TableWidget, CardWidget, InfoBar, InfoBarPosition,
                            MessageBox)

from models import (get_expenses_by_date, update_expense, delete_expense, 
                    get_all_categories)


class DailyRecordsPage(QWidget):
    """
    每日记录页面类 - 使用 Fluent Design 风格
    提供查看、编辑和删除指定日期支出记录的功能
    可嵌入到 NavigationInterface 中使用
    """
    
    def __init__(self, sound_manager=None, parent=None):
        """
        初始化每日记录页面
        
        Args:
            sound_manager: 声音管理器实例
            parent: 父控件
        """
        super().__init__(parent)
        self.sound_manager = sound_manager
        self.selected_date = QDate.currentDate().toString("yyyy-MM-dd")  # 默认今天
        self.expenses = []
        self.categories = {}
        
        self.init_ui()
        self.load_categories()
        self.load_expenses()
    
    def init_ui(self):
        """
        初始化用户界面
        """
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 15, 20, 15)
        
        # 创建各个区域
        self.create_title_area(main_layout)
        self.create_date_selection_area(main_layout)
        self.create_records_table_area(main_layout)
        self.create_action_buttons_area(main_layout)
    
    def create_title_area(self, parent_layout):
        """
        创建紧凑的标题区域
        """
        title_card = CardWidget()
        title_layout = QHBoxLayout(title_card)
        title_layout.setContentsMargins(20, 10, 20, 10)
        title_layout.setSpacing(15)
        
        # 主标题（缩小字体）
        main_title = SubtitleLabel("每日管理 / كۈنلۈك خاتىرە باشقۇرۇش")
        
        title_layout.addWidget(main_title)
        title_layout.addStretch()
        
        parent_layout.addWidget(title_card)
    
    def create_date_selection_area(self, parent_layout):
        """
        创建日期选择区域
        """
        date_card = CardWidget()
        date_layout = QHBoxLayout(date_card)
        date_layout.setContentsMargins(25, 15, 25, 15)
        date_layout.setSpacing(20)
        
        # 日期选择标签
        date_label = SubtitleLabel("选择日期 / چېسلا تاللاڭ:")
        date_label.setMinimumWidth(150)
        date_label.setFixedWidth(150)
        
        # 日期选择器
        self.date_selector = DateEdit()
        self.date_selector.setDate(QDate.currentDate())
        self.date_selector.setCalendarPopup(True)
        self.date_selector.setMinimumWidth(250)  # 增加宽度以显示完整日期
        self.date_selector.setMaximumWidth(300)
        self.date_selector.dateChanged.connect(self.on_date_changed)
        
        # 加载按钮
        load_btn = PrimaryPushButton("加载记录")
        load_btn.setMinimumHeight(35)
        load_btn.setMinimumWidth(150)
        load_btn.clicked.connect(self.load_expenses)
        
        # 连接加载按钮音效
        if self.sound_manager:
            load_btn.clicked.connect(self.sound_manager.play_click)
        
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_selector)
        date_layout.addWidget(load_btn)
        date_layout.addStretch()
        
        parent_layout.addWidget(date_card)
    
    def on_date_changed(self, date):
        """
        处理日期改变事件
        
        Args:
            date (QDate): 新选择的日期
        """
        self.selected_date = date.toString("yyyy-MM-dd")
        self.load_expenses()
    

    
    def create_records_table_area(self, parent_layout):
        """
        创建记录表格区域
        """
        table_card = CardWidget()
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(25, 20, 25, 20)
        table_layout.setSpacing(15)
        
        # 表格标题
        table_title = SubtitleLabel("支出记录详情 / چىقىم خاتىرىسى تەپسىلاتى")
        table_layout.addWidget(table_title)
        
        # 创建表格
        self.records_table = TableWidget()
        self.records_table.setColumnCount(7)
        self.records_table.setHorizontalHeaderLabels([
            "ID", "时间 / ۋاقىت", "分类 / تۈر", "金额 / پۇل", 
            "备注 / ئىزاھات", "操作员 / مەشغۇلاتچى", "操作 / مەشغۇلات"
        ])
        
        # 设置表格属性
        self.records_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.records_table.setAlternatingRowColors(True)
        self.records_table.setSortingEnabled(True)
        self.records_table.setMinimumHeight(400)  # 减少高度为总计行留空间
        
        # 连接双击事件
        self.records_table.cellDoubleClicked.connect(self.on_cell_double_clicked)
        
        # 设置列宽
        header = self.records_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)  # 时间
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # 分类
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # 金额
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)  # 备注
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)  # 操作员
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)  # 操作
        
        self.records_table.setColumnWidth(0, 60)   # ID
        self.records_table.setColumnWidth(1, 120)  # 时间
        self.records_table.setColumnWidth(2, 150)  # 分类
        self.records_table.setColumnWidth(3, 100)  # 金额
        self.records_table.setColumnWidth(4, 150)  # 备注
        self.records_table.setColumnWidth(5, 120)  # 操作员
        self.records_table.setColumnWidth(6, 200)  # 操作
        
        table_layout.addWidget(self.records_table)
        
        # 创建固定的总计行
        self.create_fixed_total_row(table_layout)
        
        parent_layout.addWidget(table_card)
    
    def create_fixed_total_row(self, parent_layout):
        """
        创建固定在底部的总计行
        """
        # 创建总计行容器
        total_container = QWidget()
        total_container.setFixedHeight(40)
        total_container.setStyleSheet("background-color: lightgray; border: 1px solid #ccc;")
        
        total_layout = QHBoxLayout(total_container)
        total_layout.setContentsMargins(0, 0, 0, 0)
        total_layout.setSpacing(0)
        
        # 创建与表格列对应的标签，使用固定宽度与表格列对齐
        self.total_id_label = BodyLabel("总计")
        self.total_id_label.setFixedWidth(60)
        self.total_id_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.total_id_label.setStyleSheet("border-right: 1px solid #ccc; padding: 5px;")
        
        self.total_time_label = BodyLabel("0条记录")
        self.total_time_label.setFixedWidth(120)
        self.total_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.total_time_label.setStyleSheet("border-right: 1px solid #ccc; padding: 5px;")
        
        self.total_category_label = BodyLabel("جەمئىي")
        self.total_category_label.setFixedWidth(150)
        self.total_category_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.total_category_label.setStyleSheet("border-right: 1px solid #ccc; padding: 5px;")
        
        self.total_amount_display_label = BodyLabel("¥0.00")
        self.total_amount_display_label.setFixedWidth(100)
        self.total_amount_display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.total_amount_display_label.setStyleSheet("border-right: 1px solid #ccc; padding: 5px; font-weight: bold;")
        
        self.total_note_label = BodyLabel("¥0.00")
        self.total_note_label.setFixedWidth(150)
        self.total_note_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.total_note_label.setStyleSheet("border-right: 1px solid #ccc; padding: 5px;")
        
        self.total_user_label = BodyLabel("0 خاتىرە")
        self.total_user_label.setFixedWidth(120)
        self.total_user_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.total_user_label.setStyleSheet("border-right: 1px solid #ccc; padding: 5px;")
        
        self.total_action_label = BodyLabel("---")
        self.total_action_label.setFixedWidth(200)
        self.total_action_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.total_action_label.setStyleSheet("padding: 5px;")
        
        total_layout.addWidget(self.total_id_label)
        total_layout.addWidget(self.total_time_label)
        total_layout.addWidget(self.total_category_label)
        total_layout.addWidget(self.total_amount_display_label)
        total_layout.addWidget(self.total_note_label)
        total_layout.addWidget(self.total_user_label)
        total_layout.addWidget(self.total_action_label)
        
        parent_layout.addWidget(total_container)
    
    def create_action_buttons_area(self, parent_layout):
        """
        创建简单统计信息区域（已移除操作按钮）
        """
        stats_card = CardWidget()
        stats_layout = QHBoxLayout(stats_card)
        stats_layout.setContentsMargins(25, 15, 25, 15)
        stats_layout.setSpacing(20)
        
        # 简单统计信息行
        # 总记录数
        self.total_records_label = BodyLabel("总记录数: 0 / جەمئىي خاتىرە سانى: 0")
        
        # 总金额
        self.total_amount_label = BodyLabel("总金额: ¥0.00 / جەمئىي پۇل مىقدارى: ¥0.00")
        
        stats_layout.addWidget(self.total_records_label)
        stats_layout.addWidget(self.total_amount_label)
        stats_layout.addStretch()
        
        parent_layout.addWidget(stats_card)
    
    def load_categories(self):
        """
        加载分类数据
        """
        try:
            categories = get_all_categories()
            self.categories = {cat['id']: cat for cat in categories}
        except Exception as e:
            InfoBar.error(
                title="加载失败 / يۈكلەش مەغلۇب بولدى",
                content=f"无法加载分类数据：{str(e)}\nتۈر مەلۇماتىنى يۈكلىيەلمىدى: {str(e)}",
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def load_expenses(self):
        """
        加载指定日期的支出记录
        """
        try:
            # 获取日期
            current_date = self.date_selector.date().toString("yyyy-MM-dd")
            self.selected_date = current_date
            
            # 获取支出记录
            self.expenses = get_expenses_by_date(current_date)
            
            # 更新表格和统计
            self.update_table()
            self.update_summary()
            
            InfoBar.success(
                title="加载完成 / يۈكلەش تاماملاندى",
                content=f"成功加载 {len(self.expenses)} 条记录\nمۇۋەپپەقىيەتلىك يۈكلەندى {len(self.expenses)} خاتىرە",
                duration=2000,
                position=InfoBarPosition.TOP,
                parent=self
            )
        except Exception as e:
            InfoBar.error(
                title="加载失败 / يۈكلەش مەغلۇب بولدى",
                content=f"无法加载记录：{str(e)}\nخاتىرىنى يۈكلىيەلمىدى: {str(e)}",
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def update_table(self):
        """
        更新记录表格
        """
        try:
            # 设置行数：只显示数据行，不包含总计行
            self.records_table.setRowCount(len(self.expenses))
            
            # 填充数据行
            for row, expense in enumerate(self.expenses):
                # expense 现在是字典格式
                expense_id = expense['id']
                category_name_cn = expense['category_name_cn']
                amount = expense['amount']
                note = expense['notes']
                username = expense['username']
                time_str = expense['expense_date']  # 使用日期作为时间显示
                
                # 获取分类的维语名称
                category_ug = expense.get('category_name_ug', self.get_category_ug_name(category_name_cn))
                
                # 填充表格数据 - 设置不可编辑项
                id_item = QTableWidgetItem(str(expense_id))
                id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # 不可编辑
                self.records_table.setItem(row, 0, id_item)
                
                time_item = QTableWidgetItem(time_str)
                time_item.setFlags(time_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # 不可编辑
                self.records_table.setItem(row, 1, time_item)
                
                category_item = QTableWidgetItem(f"{category_name_cn} / {category_ug}")
                category_item.setFlags(category_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # 不可编辑
                self.records_table.setItem(row, 2, category_item)
                
                # 金额和备注可编辑
                amount_item = QTableWidgetItem(f"{float(amount):.2f}")
                self.records_table.setItem(row, 3, amount_item)
                
                note_item = QTableWidgetItem(note or "")
                self.records_table.setItem(row, 4, note_item)
                
                user_item = QTableWidgetItem(username)
                user_item.setFlags(user_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # 不可编辑
                self.records_table.setItem(row, 5, user_item)
                
                # 创建操作按钮
                self.create_action_buttons(row, expense_id)
            
            # 更新固定的总计行显示
            self.update_fixed_total_row()
                
        except Exception as e:
            InfoBar.error(
                title="更新失败 / يېڭىلاش مەغلۇب بولدى",
                content=f"无法更新表格：{str(e)}\nجەدۋەلنى يېڭىلىيالمىدى: {str(e)}",
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def update_fixed_total_row(self):
        """
        更新固定的总计行显示
        """
        total_records = len(self.expenses)
        total_amount = sum(float(expense['amount']) for expense in self.expenses) if self.expenses else 0.0
        
        # 更新各个标签的文本
        self.total_time_label.setText(f"{total_records}条记录")
        self.total_amount_display_label.setText(f"¥{total_amount:.2f}")
        self.total_note_label.setText(f"¥{total_amount:.2f}")
        self.total_user_label.setText(f"{total_records} خاتىرە")
    
    def get_table_data_with_total(self):
        """
        获取包含总计行的完整表格数据（用于导出等功能）
        
        Returns:
            list: 包含所有数据行和总计行的列表
        """
        data = []
        
        # 添加数据行
        for expense in self.expenses:
            category_name_cn = expense['category_name_cn']
            category_ug = expense.get('category_name_ug', self.get_category_ug_name(category_name_cn))
            
            data.append([
                str(expense['id']),
                expense['expense_date'],
                f"{category_name_cn} / {category_ug}",
                f"{float(expense['amount']):.2f}",
                expense['notes'] or "",
                expense['username'],
                "操作按钮"  # 导出时用文本代替按钮
            ])
        
        # 添加总计行
        total_records = len(self.expenses)
        total_amount = sum(float(expense['amount']) for expense in self.expenses) if self.expenses else 0.0
        
        data.append([
            "总计",
            f"{total_records}条记录",
            "جەمئىي",
            f"¥{total_amount:.2f}",
            f"¥{total_amount:.2f}",
            f"{total_records} خاتىرە",
            "---"
        ])
        
        return data
    
    def create_action_buttons(self, row, expense_id):
        """
        创建操作按钮
        
        Args:
            row (int): 表格行索引
            expense_id (int): 支出记录ID
        """
        # 创建按钮容器
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(5, 2, 5, 2)
        button_layout.setSpacing(5)
        
        # 更新按钮
        update_btn = PushButton("更新")
        update_btn.setMaximumHeight(30)
        update_btn.setMaximumWidth(50)
        update_btn.setStyleSheet("background-color: #1A5319; color: white; border: none; border-radius: 4px;")
        update_btn.clicked.connect(lambda: self.update_expense(expense_id, row))
        
        # 删除按钮
        delete_btn = PushButton("删除")
        delete_btn.setMaximumHeight(30)
        delete_btn.setMaximumWidth(50)
        delete_btn.setStyleSheet("background-color: #1A5319; color: white; border: none; border-radius: 4px;")
        delete_btn.clicked.connect(lambda: self.delete_expense(expense_id))
        
        button_layout.addWidget(update_btn)
        button_layout.addWidget(delete_btn)
        
        # 设置到表格
        self.records_table.setCellWidget(row, 6, button_widget)
    
    def get_category_ug_name(self, category_cn_name):
        """
        根据中文分类名称获取维语分类名称
        
        Args:
            category_cn_name (str): 中文分类名称
            
        Returns:
            str: 维语分类名称
        """
        for cat_id, cat_info in self.categories.items():
            if cat_info['name_cn'] == category_cn_name:
                return cat_info['name_ug']
        return "نامەلۇم تۈر"
    
    def update_summary(self):
        """
        更新统计信息
        """
        total_records = len(self.expenses)
        total_amount = sum(float(expense['amount']) for expense in self.expenses)
        
        self.total_records_label.setText(f"总记录数: {total_records} / جەمئىي خاتىرە سانى: {total_records}")
        self.total_amount_label.setText(f"总金额: ¥{total_amount:.2f} / جەمئىي پۇل مىقدارى: ¥{total_amount:.2f}")
    
    def on_cell_double_clicked(self, row, column):
        """
        处理单元格双击事件，只允许编辑金额和备注
        
        Args:
            row (int): 行索引
            column (int): 列索引
        """
        # 只允许编辑金额(列3)和备注(列4)
        if column == 3:  # 金额列
            InfoBar.info(
                title="提示 / ئەسكەرتىش",
                content="双击可编辑金额，编辑完成后点击更新按钮保存\nپۇل مىقدارىنى تەھرىرلەش ئۈچۈن قوش چېكىڭ، تاماملانغاندىن كېيىن يېڭىلاش كۇنۇپكىسىنى بېسىپ ساقلاڭ",
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
        elif column == 4:  # 备注列
            InfoBar.info(
                title="提示 / ئەسكەرتىش",
                content="双击可编辑备注，编辑完成后点击更新按钮保存\nئىزاھاتنى تەھرىرلەش ئۈچۈن قوش چېكىڭ، تاماملانغاندىن كېيىن يېڭىلاش كۇنۇپكىسىنى بېسىپ ساقلاڭ",
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
        else:
            InfoBar.warning(
                title="无法编辑 / تەھرىرلىيالمايدۇ",
                content="只能编辑金额和备注，其他字段不可修改\nپەقەت پۇل مىقدارى ۋە ئىزاھاتنىلا تەھرىرلىگىلى بولىدۇ",
                duration=2000,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def update_expense(self, expense_id, row):
        """
        更新支出记录
        
        Args:
            expense_id (int): 支出记录ID
            row (int): 表格行索引
        """
        try:
            # 从表格获取新的金额和备注
            amount_item = self.records_table.item(row, 3)
            note_item = self.records_table.item(row, 4)
            
            if not amount_item:
                InfoBar.warning(
                    title="无法更新 / يېڭىلىيالمايدۇ",
                    content="金额不能为空\nپۇل مىقدارى بوش بولۇشى مۇمكىن ئەمەس",
                    duration=2000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                return
            
            try:
                # 尝试转换金额
                amount_text = amount_item.text().strip()
                amount = float(amount_text)
                if amount <= 0:
                    InfoBar.warning(
                        title="金额错误 / پۇل مىقدارى خاتا",
                        content="金额必须大于0\nپۇل مىقدارى 0 دىن چوڭ بولۇشى كېرەك",
                        duration=2000,
                        position=InfoBarPosition.TOP,
                        parent=self
                    )
                    return
            except ValueError:
                InfoBar.warning(
                    title="金额格式错误 / پۇل مىقدارى فورماتى خاتا",
                    content="请输入有效的数字\nئىناۋەتلىك سان كىرگۈزۈڭ",
                    duration=2000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                return
            
            note = note_item.text().strip() if note_item else ""
            
            # 调用更新函数
            success = update_expense(expense_id, amount, note)
            
            if success:
                InfoBar.success(
                    title="更新成功 / يېڭىلاش مۇۋەپپەقىيەتلىك",
                    content="记录已成功更新\nخاتىرە مۇۋەپپەقىيەتلىك يېڭىلاندى",
                    duration=2000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                
                # 重新加载数据以确保同步
                self.load_expenses()
            else:
                InfoBar.error(
                    title="更新失败 / يېڭىلاش مەغلۇب بولدى",
                    content="无法更新记录\nخاتىرىنى يېڭىلىيالمىدى",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                
        except Exception as e:
            InfoBar.error(
                title="更新失败 / يېڭىلاش مەغلۇب بولدى",
                content=f"更新记录时发生错误：{str(e)}\nخاتىرىنى يېڭىلاش مەغلۇب بولدى: {str(e)}",
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def delete_expense(self, expense_id):
        """
        删除支出记录
        
        Args:
            expense_id (int): 支出记录ID
        """
        try:
            # 确认删除
            reply = MessageBox(
                "确认删除 / ئۆچۈرۈشنى جەزملەش",
                f"确定要删除这条记录吗？\nبۇ خاتىرىنى راستىنلا ئۆچۈرەمسىز؟",
                self
            )
            reply.yesButton.setText("确定")
            reply.cancelButton.setText("取消")
            
            if reply.exec():
                # 执行删除
                success = delete_expense(expense_id)
                
                if success:
                    InfoBar.success(
                        title="删除成功 / ئۆچۈرۈش مۇۋەپپەقىيەتلىك",
                        content="记录已成功删除\nخاتىرە مۇۋەپپەقىيەتلىك ئۆچۈرۈلدى",
                        duration=2000,
                        position=InfoBarPosition.TOP,
                        parent=self
                    )
                    
                    # 重新加载数据
                    self.load_expenses()
                else:
                    InfoBar.warning(
                        title="删除失败 / ئۆچۈرۈش مەغلۇب بولدى",
                        content="记录删除失败\nخاتىرە ئۆچۈرۈش مەغلۇب بولدى",
                        duration=3000,
                        position=InfoBarPosition.TOP,
                        parent=self
                    )
                    
        except Exception as e:
            InfoBar.error(
                title="删除失败 / ئۆچۈرۈش مەغلۇب بولدى",
                content=f"无法删除记录：{str(e)}\nخاتىرىنى ئۆچۈرەلمىدى: {str(e)}",
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
 