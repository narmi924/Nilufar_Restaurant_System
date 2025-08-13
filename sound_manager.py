#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美莲花美食支出记录系统 - 声音管理器
用于管理应用程序中所有UI音效的中央管理器
提供统一的音效播放接口，支持点击、确认、弹出和警告等音效
采用懒加载模式，解决首次播放时所有音效同时播放的bug
支持音效开关机制，避免初始化阶段的意外触发
"""

import os
from PyQt6.QtCore import QObject, QUrl
from PyQt6.QtMultimedia import QSoundEffect
from database import get_resource_path


class SoundManager(QObject):
    """
    声音管理器类 - 管理应用程序中的所有UI音效
    
    采用懒加载策略：
    - 在初始化时只存储音效文件路径，不创建QSoundEffect实例
    - 在首次播放时才创建对应的QSoundEffect实例并缓存
    - 后续播放直接从缓存获取实例，实现高效播放
    - 彻底解决Qt音频后端首次激活时的"广播效应"问题
    
    支持音效开关机制：
    - 可以临时禁用音效，避免初始化阶段的意外触发
    - 提供enable_sounds()和disable_sounds()方法控制音效状态
    """
    
    def __init__(self, parent=None):
        """
        初始化声音管理器 - 懒加载模式
        
        Args:
            parent: 父对象，用于Qt对象层次结构管理
        """
        super().__init__(parent)
        
        # 音效开关状态 - 默认启用
        self._sounds_enabled = True
        
        # 音效文件路径字典 - 存储音效名到文件路径的映射
        self.sound_paths = {}
        
        # 音效实例缓存字典 - 存储已创建的QSoundEffect实例
        self.sound_cache = {}
        
        # 获取兼容模式下的sounds文件夹路径
        sounds_dir = get_resource_path('sounds')
        
        # 定义所有音效文件名列表
        sound_files = [
            'click.wav',        # 点击音效
            'confirmation.wav', # 确认音效
            'pop.wav',         # 弹出音效
            'warning.wav'      # 警告音效
        ]
        
        # 构建音效文件路径映射
        self._build_sound_paths(sounds_dir, sound_files)
    
    def enable_sounds(self):
        """启用音效播放"""
        self._sounds_enabled = True
    
    def disable_sounds(self):
        """禁用音效播放"""
        self._sounds_enabled = False
    
    def is_sounds_enabled(self):
        """检查音效是否启用"""
        return self._sounds_enabled
    
    def _build_sound_paths(self, sounds_dir, sound_files):
        """
        构建音效文件路径映射
        
        Args:
            sounds_dir (str): 音效文件目录路径
            sound_files (list): 音效文件名列表
        """
        # 检查音效目录是否存在
        if not os.path.exists(sounds_dir):
            return
        
        # 遍历音效文件列表，构建路径映射
        for sound_file in sound_files:
            # 构建完整的文件路径
            file_path = os.path.join(sounds_dir, sound_file)
            
            # 检查文件是否存在
            if os.path.exists(file_path):
                # 提取不带扩展名的文件名作为键
                effect_name = os.path.splitext(sound_file)[0]
                
                # 存储文件路径到路径字典中
                self.sound_paths[effect_name] = file_path
    
    def play_click(self):
        """播放点击音效 - 懒加载模式"""
        # 检查音效是否启用
        if not self._sounds_enabled:
            return
            
        sound_name = 'click'
        # 检查缓存中是否已有此音效实例
        if sound_name not in self.sound_cache:
            # 如果没有，则创建实例并存入缓存
            if sound_name in self.sound_paths:
                try:
                    effect = QSoundEffect(self)
                    effect.setSource(QUrl.fromLocalFile(self.sound_paths[sound_name]))
                    self.sound_cache[sound_name] = effect
                except Exception:
                    # 静默处理创建失败的情况
                    return
        
        # 从缓存中获取实例并播放
        if sound_name in self.sound_cache:
            try:
                self.sound_cache[sound_name].play()
            except Exception:
                # 静默处理播放失败的情况
                pass
    
    def play_confirmation(self):
        """播放确认音效 - 懒加载模式"""
        # 检查音效是否启用
        if not self._sounds_enabled:
            return
            
        sound_name = 'confirmation'
        # 检查缓存中是否已有此音效实例
        if sound_name not in self.sound_cache:
            # 如果没有，则创建实例并存入缓存
            if sound_name in self.sound_paths:
                try:
                    effect = QSoundEffect(self)
                    effect.setSource(QUrl.fromLocalFile(self.sound_paths[sound_name]))
                    self.sound_cache[sound_name] = effect
                except Exception:
                    # 静默处理创建失败的情况
                    return
        
        # 从缓存中获取实例并播放
        if sound_name in self.sound_cache:
            try:
                self.sound_cache[sound_name].play()
            except Exception:
                # 静默处理播放失败的情况
                pass
    
    def play_pop(self):
        """播放弹出音效 - 懒加载模式"""
        # 检查音效是否启用
        if not self._sounds_enabled:
            return
            
        sound_name = 'pop'
        # 检查缓存中是否已有此音效实例
        if sound_name not in self.sound_cache:
            # 如果没有，则创建实例并存入缓存
            if sound_name in self.sound_paths:
                try:
                    effect = QSoundEffect(self)
                    effect.setSource(QUrl.fromLocalFile(self.sound_paths[sound_name]))
                    self.sound_cache[sound_name] = effect
                except Exception:
                    # 静默处理创建失败的情况
                    return
        
        # 从缓存中获取实例并播放
        if sound_name in self.sound_cache:
            try:
                self.sound_cache[sound_name].play()
            except Exception:
                # 静默处理播放失败的情况
                pass
    
    def play_warning(self):
        """播放警告音效 - 懒加载模式"""
        # 检查音效是否启用
        if not self._sounds_enabled:
            return
            
        sound_name = 'warning'
        # 检查缓存中是否已有此音效实例
        if sound_name not in self.sound_cache:
            # 如果没有，则创建实例并存入缓存
            if sound_name in self.sound_paths:
                try:
                    effect = QSoundEffect(self)
                    effect.setSource(QUrl.fromLocalFile(self.sound_paths[sound_name]))
                    self.sound_cache[sound_name] = effect
                except Exception:
                    # 静默处理创建失败的情况
                    return
        
        # 从缓存中获取实例并播放
        if sound_name in self.sound_cache:
            try:
                self.sound_cache[sound_name].play()
            except Exception:
                # 静默处理播放失败的情况
                pass
