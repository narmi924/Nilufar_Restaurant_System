#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美莲花美食支出记录系统 - 主程序
处理应用程序启动和窗口间的跳转
"""

import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMessageBox
from qfluentwidgets import setTheme, Theme, FluentTranslator, setThemeColor
from login_window import LoginWindow
from main_window import MainWindow
from sound_manager import SoundManager


class RestaurantApp:
    """
    美莲花美食应用程序主类
    负责管理整个应用程序的生命周期和窗口跳转
    """
    
    def __init__(self):
        """
        初始化应用程序
        """
        # 创建QApplication实例
        self.app = QApplication(sys.argv)
        
        # 创建全局声音管理器
        self.sound_manager = SoundManager()
        
        # 设置Fluent主题
        setTheme(Theme.LIGHT)
        setThemeColor('#1A5319')
        translator = FluentTranslator()
        self.app.installTranslator(translator)
        
        # 设置应用程序样式和名称
        self.app.setStyle('Fusion')
        self.app.setApplicationName("美莲花美食支出记录系统")
        self.app.setApplicationDisplayName("美莲花美食支出记录系统 / نىلۇپەر تائاملار سارىيى چىقىم خاتىرىسى سىستېمىسى")
        
        # 初始化窗口变量
        self.login_window = None
        self.main_window = None
        self.current_username = None
        self.current_user_role = None
    
    def run(self):
        """
        启动应用程序
        """
        # 首先显示登录窗口
        self.show_login_window()
        
        # 启动事件循环
        return self.app.exec()
    
    def show_login_window(self):
        """显示登录窗口"""
        self.login_window = LoginWindow(self.sound_manager)
        self.login_window.login_successful.connect(self.on_login_successful)
        self.login_window.show()
        self.login_window.raise_()
        self.login_window.activateWindow()
    
    def on_login_successful(self, user_role):
        """处理登录成功事件"""
        self.current_username = self.login_window.username_input.text().strip()
        self.current_user_role = user_role
        
        if self.login_window:
            self.login_window.close()
            self.login_window = None
        
        self.show_main_window()
    
    def show_main_window(self):
        """显示主窗口"""
        try:
            self.main_window = MainWindow(self.current_username, self.current_user_role, self.sound_manager)
            self.main_window.destroyed.connect(self.on_main_window_closed)
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()
            
        except Exception as e:
            error_box = QMessageBox()
            error_box.setIcon(QMessageBox.Icon.Critical)
            error_box.setWindowTitle("系统错误 / سىستېما خاتالىقى")
            error_box.setText(f"无法打开主窗口：{str(e)}\nئاساسىي كۆزنەكنى ئاچالمايدۇ: {str(e)}")
            error_box.addButton("确定", QMessageBox.ButtonRole.AcceptRole)
            error_box.exec()
            self.show_login_window()
    
    def on_main_window_closed(self):
        """处理主窗口关闭事件"""
        self.main_window = None
        self.current_username = None
        self.current_user_role = None
        self.app.quit()
    
    def show_message(self, title, message, msg_type="info"):
        """显示消息对话框"""
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        icon_map = {
            "warning": QMessageBox.Icon.Warning,
            "error": QMessageBox.Icon.Critical,
            "success": QMessageBox.Icon.Information
        }
        msg_box.setIcon(icon_map.get(msg_type, QMessageBox.Icon.Information))
        msg_box.addButton("确定", QMessageBox.ButtonRole.AcceptRole)
        msg_box.exec()


def main():
    """程序主入口"""
    try:
        # 初始化数据库
        from database import initialize_database
        initialize_database()
        
        # 创建并运行应用程序
        restaurant_app = RestaurantApp()
        sys.exit(restaurant_app.run())
        
    except Exception as e:

        try:
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
            
            startup_error_box = QMessageBox()
            startup_error_box.setIcon(QMessageBox.Icon.Critical)
            startup_error_box.setWindowTitle("启动失败 / قوزغىتىش مەغلۇب بولدى")
            startup_error_box.setText(f"应用程序启动失败：{str(e)}\nئەپ قوزغىتىش مەغلۇب بولدى: {str(e)}")
            startup_error_box.addButton("确定", QMessageBox.ButtonRole.AcceptRole)
            startup_error_box.exec()
        except:

            pass
        
        sys.exit(1)


if __name__ == "__main__":
    main() 