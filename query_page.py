#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美莲花美食支出记录系统 - 查询页面
基于 Fluent Design 的功能页面，可嵌入到 NavigationInterface 中
"""

import sys
import pandas as pd
from datetime import datetime, timedelta
from PyQt6.QtCore import Qt, QDate, QTimer
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QHeaderView, QAbstractItemView, QTableWidgetItem, QFileDialog, QSplitter)
from qfluentwidgets import (TitleLabel, SubtitleLabel, BodyLabel, 
                            DateEdit, ComboBox, PrimaryPushButton, PushButton, 
                            TableWidget, CardWidget, InfoBar, InfoBarPosition)

from models import get_expenses_by_date_range, get_all_categories


class QueryPage(QWidget):
    """
    查询页面类 - 使用 Fluent Design 风格
    支持按日期范围和分类查询支出记录
    可嵌入到 NavigationInterface 中使用
    """
    
    def __init__(self, sound_manager=None, parent=None):
        """
        初始化查询页面
        
        Args:
            sound_manager: 声音管理器实例
            parent: 父控件
        """
        super().__init__(parent)
        self.sound_manager = sound_manager
        self.query_results = []
        
        # 初始化UI
        self.init_ui()
        
        # 加载分类数据
        self.load_categories()
        
        # 连接事件处理器
        self.connect_events()
        
        # 自动执行初始查询
        QTimer.singleShot(200, self.handle_query)
        
    def init_ui(self):
        """
        初始化用户界面 - 使用优化的分栏布局
        """
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 10, 15, 10)
        
        # 创建头部区域：标题和查询条件
        self.create_header_section(main_layout)
        
        # 创建内容区域：统计信息和查询结果
        self.create_content_section(main_layout)

    def create_header_section(self, parent_layout):
        """
        创建页面头部区域 - 标题和查询条件
        """
        header_card = CardWidget()
        header_layout = QVBoxLayout(header_card)
        header_layout.setContentsMargins(25, 20, 25, 20)
        header_layout.setSpacing(20)
        
        # 页面标题行
        title_layout = QHBoxLayout()
        main_title = SubtitleLabel("查询记录 / خاتىرە كۆرۈش ")
        main_title.setObjectName("pageTitle")
        title_layout.addWidget(main_title)
        title_layout.addStretch()
        header_layout.addLayout(title_layout)
        
        # 查询条件行
        conditions_layout = QHBoxLayout()
        conditions_layout.setSpacing(25)
        
        # 开始日期
        start_label = BodyLabel("开始日期:")
        start_label.setMinimumWidth(70)
        self.start_date_edit = DateEdit()
        self.start_date_edit.setDate(QDate.currentDate().addDays(-30))
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setMinimumWidth(200)
        self.start_date_edit.setMaximumWidth(250)
        
        # 结束日期
        end_label = BodyLabel("结束日期:")
        end_label.setMinimumWidth(70)
        self.end_date_edit = DateEdit()
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setMinimumWidth(200)
        self.end_date_edit.setMaximumWidth(250)
        
        # 分类筛选
        category_label = BodyLabel("支出分类:")
        category_label.setMinimumWidth(70)
        self.category_combo = ComboBox()
        self.category_combo.setMinimumWidth(200)
        self.category_combo.setMaximumWidth(280)
        
        # 查询按钮
        query_btn = PrimaryPushButton("查询记录")
        query_btn.setFixedSize(100, 32)
        query_btn.clicked.connect(self.handle_query)
        
        # 连接查询按钮音效
        if self.sound_manager:
            query_btn.clicked.connect(self.sound_manager.play_click)
        
        conditions_layout.addWidget(start_label)
        conditions_layout.addWidget(self.start_date_edit)
        conditions_layout.addWidget(end_label)
        conditions_layout.addWidget(self.end_date_edit)
        conditions_layout.addWidget(category_label)
        conditions_layout.addWidget(self.category_combo)
        conditions_layout.addWidget(query_btn)
        conditions_layout.addStretch()
        
        header_layout.addLayout(conditions_layout)
        parent_layout.addWidget(header_card)

    def create_content_section(self, parent_layout):
        """
        创建内容区域 - 统计信息和查询结果表格
        """
        # 使用水平分割器实现灵活布局
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：统计信息和操作按钮
        self.create_stats_panel(splitter)
        
        # 右侧：查询结果表格
        self.create_table_panel(splitter)
        
        # 设置分割比例 (25% : 75%)
        splitter.setSizes([300, 900])
        splitter.setChildrenCollapsible(False)
        
        parent_layout.addWidget(splitter, 1)

    def create_stats_panel(self, parent_splitter):
        """
        创建统计信息面板
        """
        stats_card = CardWidget()
        stats_layout = QVBoxLayout(stats_card)
        stats_layout.setContentsMargins(20, 20, 20, 20)
        stats_layout.setSpacing(20)
        
        # 统计信息标题
        stats_title = SubtitleLabel("查询摘要")
        stats_layout.addWidget(stats_title)
        
        # 统计数据显示区域
        self.stats_container = QWidget()
        stats_data_layout = QVBoxLayout(self.stats_container)
        stats_data_layout.setSpacing(15)
        
        # 基本统计信息
        self.total_records_label = BodyLabel("记录数: --")
        self.total_amount_label = BodyLabel("总金额: --")
        self.avg_amount_label = BodyLabel("平均金额: --")
        self.date_range_label = BodyLabel("查询范围: --")
        
        stats_data_layout.addWidget(self.total_records_label)
        stats_data_layout.addWidget(self.total_amount_label)
        stats_data_layout.addWidget(self.avg_amount_label)
        stats_data_layout.addWidget(self.date_range_label)
        
        stats_layout.addWidget(self.stats_container)
        
        # 分隔线
        stats_layout.addWidget(BodyLabel(""))
        
        # 操作按钮区域
        self.create_action_buttons(stats_layout)
        
        stats_layout.addStretch()
        parent_splitter.addWidget(stats_card)

    def create_action_buttons(self, parent_layout):
        """
        创建操作按钮
        """
        buttons_title = BodyLabel("操作:")
        buttons_title.setStyleSheet("font-weight: bold; color: black;")
        parent_layout.addWidget(buttons_title)
        
        # 导出Excel按钮
        self.export_btn = PushButton("导出Excel")
        self.export_btn.setFixedHeight(36)
        self.export_btn.setStyleSheet("background-color: #1A5319; color: white; border: none; border-radius: 6px;")
        self.export_btn.clicked.connect(self.handle_export)
        self.export_btn.setEnabled(False)
        
        # 连接导出按钮音效
        if self.sound_manager:
            self.export_btn.clicked.connect(self.sound_manager.play_click)
        
        # 刷新数据按钮
        self.refresh_btn = PushButton("刷新数据")
        self.refresh_btn.setFixedHeight(36)
        self.refresh_btn.setStyleSheet("background-color: #1A5319; color: white; border: none; border-radius: 6px;")
        self.refresh_btn.clicked.connect(self.handle_query)
        
        # 连接刷新按钮音效
        if self.sound_manager:
            self.refresh_btn.clicked.connect(self.sound_manager.play_click)
        
        # 重置条件按钮
        self.reset_btn = PushButton("重置条件")
        self.reset_btn.setFixedHeight(36)
        self.reset_btn.setStyleSheet("background-color: #1A5319; color: white; border: none; border-radius: 6px;")
        self.reset_btn.clicked.connect(self.handle_reset)
        
        # 连接重置按钮音效
        if self.sound_manager:
            self.reset_btn.clicked.connect(self.sound_manager.play_click)
        
        parent_layout.addWidget(self.export_btn)
        parent_layout.addWidget(self.refresh_btn)
        parent_layout.addWidget(self.reset_btn)

    def create_table_panel(self, parent_splitter):
        """
        创建表格面板
        """
        table_card = CardWidget()
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(25, 20, 25, 20)
        table_layout.setSpacing(15)
        
        # 表格标题
        table_title = SubtitleLabel("查询结果 / خاتىرە نەتىجىسى") 
        table_layout.addWidget(table_title)
        
        # 创建结果表格
        self.result_table = TableWidget()
        self.result_table.setColumnCount(5)  # 删除ID列，从6列改为5列
        self.result_table.setHorizontalHeaderLabels([
            "日期", "分类", "金额", "备注", "操作员"  # 删除ID列
        ])
        
        # 设置表格属性 
        self.result_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setSortingEnabled(True)
        self.result_table.setMinimumHeight(400)  # 减少高度为总计行留空间
        
        # 设置列宽 
        header = self.result_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # 日期
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)  # 分类
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # 金额
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # 备注
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)  # 操作员
        
        self.result_table.setColumnWidth(0, 150)  # 日期
        self.result_table.setColumnWidth(1, 200)  # 分类
        self.result_table.setColumnWidth(2, 100)  # 金额
        self.result_table.setColumnWidth(3, 200)  # 备注
        self.result_table.setColumnWidth(4, 150)  # 操作员
        
        table_layout.addWidget(self.result_table)
        
        # 创建固定的总计行
        self.create_fixed_total_row_query(table_layout)
        parent_splitter.addWidget(table_card)
    
    def create_fixed_total_row_query(self, parent_layout):
        """
        创建固定在底部的总计行（查询页面）
        """
        # 创建总计行容器
        total_container = QWidget()
        total_container.setFixedHeight(40)
        total_container.setStyleSheet("background-color: lightgray; border: 1px solid #ccc;")
        
        total_layout = QHBoxLayout(total_container)
        total_layout.setContentsMargins(0, 0, 0, 0)
        total_layout.setSpacing(0)
        
        # 创建与表格列对应的标签，使用固定宽度与表格列对齐
        self.query_total_date_label = BodyLabel("总计")
        self.query_total_date_label.setFixedWidth(150)
        self.query_total_date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.query_total_date_label.setStyleSheet("border-right: 1px solid #ccc; padding: 5px;")
        
        self.query_total_category_label = BodyLabel("جەمئىي - 0条记录")
        self.query_total_category_label.setFixedWidth(200)
        self.query_total_category_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.query_total_category_label.setStyleSheet("border-right: 1px solid #ccc; padding: 5px;")
        
        self.query_total_amount_label = BodyLabel("¥0.00")
        self.query_total_amount_label.setFixedWidth(100)
        self.query_total_amount_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.query_total_amount_label.setStyleSheet("border-right: 1px solid #ccc; padding: 5px; font-weight: bold;")
        
        self.query_total_note_label = BodyLabel("¥0.00")
        self.query_total_note_label.setFixedWidth(200)
        self.query_total_note_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.query_total_note_label.setStyleSheet("border-right: 1px solid #ccc; padding: 5px;")
        
        self.query_total_operator_label = BodyLabel("0 خاتىرە")
        self.query_total_operator_label.setFixedWidth(150)
        self.query_total_operator_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.query_total_operator_label.setStyleSheet("padding: 5px;")
        
        total_layout.addWidget(self.query_total_date_label)
        total_layout.addWidget(self.query_total_category_label)
        total_layout.addWidget(self.query_total_amount_label)
        total_layout.addWidget(self.query_total_note_label)
        total_layout.addWidget(self.query_total_operator_label)
        
        parent_layout.addWidget(total_container)

    def load_categories(self):
        """
        加载分类数据到下拉框
        """
        try:
            categories = get_all_categories()
            
            # 清空现有项
            self.category_combo.clear()
            self.category_combo.addItem("全部分类", "0")
            
            # 添加分类
            for category in categories:
                display_text = f"{category['name_cn']} / {category['name_ug']}"
                self.category_combo.addItem(display_text, str(category['id']))
                
        except Exception as e:
            InfoBar.error(
                title="加载失败",
                content=f"无法加载分类数据：{str(e)}",
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def connect_events(self):
        """连接事件处理器"""
        # 连接分类选择改变事件
        self.category_combo.currentTextChanged.connect(self.on_category_changed)
        
        # 连接下拉框音效
        if self.sound_manager:
            self.category_combo.activated.connect(self.sound_manager.play_pop)
    
    def on_category_changed(self):
        """分类选择改变时的处理"""
        # 使用定时器延迟执行查询，避免初始化时的干扰
        QTimer.singleShot(50, self.handle_query)
    
    def get_category_ug_name(self, category_cn_name):
        """
        根据中文分类名称获取维语分类名称
        
        Args:
            category_cn_name (str): 中文分类名称
            
        Returns:
            str: 维语分类名称
        """
        try:
            categories = get_all_categories()
            for category in categories:
                if category['name_cn'] == category_cn_name:
                    return category['name_ug']
            return "نامەلۇم تۈر"  # 默认值
        except:
            return "نامەلۇم تۈر"  # 出错时的默认值
    
    def handle_query(self):
        """
        处理查询请求
        """
        try:
            # 获取查询条件
            start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
            end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
            
            # 验证日期范围
            if self.start_date_edit.date() > self.end_date_edit.date():
                InfoBar.warning(
                    title="日期错误",
                    content="开始日期不能晚于结束日期",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                return
            
            # 获取分类筛选 - 使用备用方案处理QFluentWidgets ComboBox的data问题
            current_index = self.category_combo.currentIndex()
            category_id_str = self.category_combo.currentData()
            
            if category_id_str is None:
                category_id_str = "0"
            
            # 获取当前选择的分类信息
            selected_category_text = self.category_combo.currentText()
            
            # 备用方案：如果选择了非全部分类但ID仍为0，通过文本匹配获取正确的分类ID
            if current_index > 0 and category_id_str == "0":
                categories = get_all_categories()
                for category in categories:
                    # 精确匹配：检查分类名称是否与选择的文本完全匹配
                    display_text = f"{category['name_cn']} / {category['name_ug']}"
                    if display_text == selected_category_text:
                        category_id_str = str(category['id'])
                        break
            
            # 查询数据
            if category_id_str == "0":
                raw_results = get_expenses_by_date_range(start_date, end_date)
                query_type = "全部分类"
            else:
                category_id = int(category_id_str)
                raw_results = get_expenses_by_date_range(start_date, end_date, category_id)
                query_type = f"分类筛选: {selected_category_text}"
            
            # 转换数据格式
            self.query_results = []
            for row in raw_results:
                self.query_results.append({
                    'date': row[0],           # expense_date
                    'category_name': row[1],  # category name_cn
                    'amount': row[2],         # amount
                    'operator': row[3],       # username
                    'description': row[4] if row[4] else '',  # notes
                })
            
            # 更新统计信息
            self.update_summary(start_date, end_date)
            
            # 更新表格
            self.update_table()
            
            # 启用导出按钮
            self.export_btn.setEnabled(len(self.query_results) > 0)
            
            InfoBar.success(
                title="查询完成",
                content=f"查询完成 ({query_type})，共找到 {len(self.query_results)} 条记录",
                duration=2000,
                position=InfoBarPosition.TOP,
                parent=self
            )
            
        except Exception as e:
            InfoBar.error(
                title="查询失败",
                content=f"查询时发生错误：{str(e)}",
                duration=4000,
                position=InfoBarPosition.TOP,
                parent=self
            )
    
    def update_summary(self, start_date, end_date):
        """
        更新统计摘要信息
        """
        total_records = len(self.query_results)
        total_amount = sum(item['amount'] for item in self.query_results)
        avg_amount = total_amount / total_records if total_records > 0 else 0
        
        # 更新标签
        self.total_records_label.setText(f"记录数: {total_records}")
        self.total_amount_label.setText(f"总金额: ¥{total_amount:.2f}")
        self.avg_amount_label.setText(f"平均金额: ¥{avg_amount:.2f}")
        self.date_range_label.setText(f"查询范围: {start_date} 至 {end_date}")
    
    def update_table(self):
        """
        更新查询结果表格 - 分类列显示双语，删除ID列
        """
        # 设置行数：只显示数据行，不包含总计行
        self.result_table.setRowCount(len(self.query_results))
        
        # 填充数据行
        for row, item in enumerate(self.query_results):
            # 获取维语分类名称
            category_ug = self.get_category_ug_name(item['category_name'])
            category_display = f"{item['category_name']} / {category_ug}"
            
            self.result_table.setItem(row, 0, QTableWidgetItem(str(item['date'])))
            self.result_table.setItem(row, 1, QTableWidgetItem(category_display))
            self.result_table.setItem(row, 2, QTableWidgetItem(f"¥{item['amount']:.2f}"))
            self.result_table.setItem(row, 3, QTableWidgetItem(item['description']))
            self.result_table.setItem(row, 4, QTableWidgetItem(item['operator']))  # 删除ID列
        
        # 更新固定的总计行显示
        self.update_fixed_total_row_query()
    
    def update_fixed_total_row_query(self):
        """
        更新固定的总计行显示（查询页面）
        """
        total_records = len(self.query_results)
        total_amount = sum(item['amount'] for item in self.query_results) if self.query_results else 0.0
        
        # 更新各个标签的文本
        self.query_total_category_label.setText(f"جەمئىي - {total_records}条记录")
        self.query_total_amount_label.setText(f"¥{total_amount:.2f}")
        self.query_total_note_label.setText(f"¥{total_amount:.2f}")
        self.query_total_operator_label.setText(f"{total_records} خاتىرە")

    def handle_export(self):
        """
        处理导出Excel请求
        """
        try:
            if not hasattr(self, 'query_results') or not self.query_results:
                InfoBar.warning(
                    title="导出提醒",
                    content="没有数据可以导出，请先进行查询",
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
                return
            
            # 获取当前筛选的时间段
            start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
            end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
            
            # 选择保存路径
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "导出查询结果",
                f"美莲花美食_{start_date}_至_{end_date}_查询结果.xlsx",
                "Excel文件 (*.xlsx)"
            )
            
            if not file_path:
                return
            
            # 创建DataFrame
            data = []
            for item in self.query_results:
                data.append([
                    item['date'],
                    item['category_name'],
                    f"¥{item['amount']:.2f}",
                    item['description'],
                    item['operator'],
                ])
            
            # 添加总计行
            total_records = len(self.query_results)
            total_amount = sum(item['amount'] for item in self.query_results) if self.query_results else 0.0
            data.append([
                "总计",
                f"جەمئىي - {total_records}条记录",
                f"¥{total_amount:.2f}",
                f"¥{total_amount:.2f}",
                f"{total_records} خاتىرە"
            ])
            
            df = pd.DataFrame(data, columns=[
                "日期", "分类", "金额", "备注", "操作员"
            ])
            
            # 导出到Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='查询结果', index=False)
                
                # 设置列宽
                worksheet = writer.sheets['查询结果']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 30)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            InfoBar.success(
                title="导出成功",
                content=f"查询结果已成功导出到：\n{file_path}",
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )
            
        except Exception as e:
            InfoBar.error(
                title="导出失败",
                content=f"导出时发生错误：{str(e)}",
                duration=4000,
                position=InfoBarPosition.TOP,
                parent=self
            )

    def handle_reset(self):
        """
        重置查询条件
        """
        # 重置日期
        self.start_date_edit.setDate(QDate.currentDate().addDays(-30))
        self.end_date_edit.setDate(QDate.currentDate())
        
        # 重置分类
        self.category_combo.setCurrentIndex(0)
        
        # 清空表格
        self.result_table.setRowCount(0)
        
        # 重置统计信息
        self.total_records_label.setText("记录数: --")
        self.total_amount_label.setText("总金额: --")
        self.avg_amount_label.setText("平均金额: --")
        self.date_range_label.setText("查询范围: --")
        
        # 重置固定总计行
        self.query_total_category_label.setText("جەمئىي - 0条记录")
        self.query_total_amount_label.setText("¥0.00")
        self.query_total_note_label.setText("¥0.00")
        self.query_total_operator_label.setText("0 خاتىرە")
        
        # 禁用导出按钮
        self.export_btn.setEnabled(False)
        
        # 清空查询结果
        if hasattr(self, 'query_results'):
            self.query_results = []
        
        InfoBar.success(
            title="重置完成",
            content="查询条件已重置",
            duration=2000,
            position=InfoBarPosition.TOP,
            parent=self
        ) 