# -*- coding: utf-8 -*-
"""
美莲花餐厅支出记录系统 - 多线程Worker模块
提供在后台线程中执行DeepSeek AI分析任务的Worker类，避免UI阻塞
"""

import configparser
import os
import sys
from PyQt6.QtCore import QObject, pyqtSignal
from openai import OpenAI



class AIAnalysisWorker(QObject):
    """
    AI分析Worker类 - 在后台线程中执行DeepSeek AI分析任务
    
    继承自QObject，可以在QThread中运行，通过信号与主线程通信
    """
    
    # 定义信号
    finished = pyqtSignal(str)  # 成功获取到AI报告时发射，携带报告字符串
    error = pyqtSignal(str)     # 发生错误时发射，携带错误信息字符串
    
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
    
    def run_analysis(self, period1_data, period1_dates, period2_data, period2_dates):
        """
        在后台线程中执行AI分析任务
        
        Args:
            period1_data (list): 第一时段的分类汇总数据 [{'category_cn': '羊肉', 'total_amount': 1250.50}, ...]
            period1_dates (tuple): 第一时段的日期范围 ('2025-01-01', '2025-01-15')
            period2_data (list): 第二时段的分类汇总数据
            period2_dates (tuple): 第二时段的日期范围 ('2025-01-16', '2025-01-31')
        """
        
        try:
            # 1. 加载API密钥
            config = configparser.ConfigParser()
            # 保持选项名大小写
            config.optionxform = str
            config_path = self.get_config_path()
            
            if not os.path.exists(config_path):
                error_message = "❌ 认证失败：API密钥无效或已过期\n请更新config.ini中的DEEPSEEK_API_KEY"
                self.error.emit(error_message)
                return
            
            config.read(config_path, encoding='utf-8')
            
            # 获取API密钥
            api_key = None
            if config.has_section('DEEPSEEK'):
                if config.has_option('DEEPSEEK', 'API_KEY'):
                    api_key = config.get('DEEPSEEK', 'API_KEY').strip()
                elif config.has_option('DEEPSEEK', 'api_key'):
                    api_key = config.get('DEEPSEEK', 'api_key').strip()
            elif config.has_section('API') and config.has_option('API', 'DEEPSEEK_API_KEY'):
                api_key = config.get('API', 'DEEPSEEK_API_KEY').strip()
            
            if not api_key or api_key == 'sk-':
                error_message = "❌ 认证失败：API密钥无效或已过期\n请更新config.ini中的DEEPSEEK_API_KEY"
                self.error.emit(error_message)
                return
            
            # 2. 初始化OpenAI客户端（使用DeepSeek的API端点）
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com/v1",
                timeout=90.0  # 增加到90秒超时，适应AI深度分析需求
            )
            
            # 3. 格式化数据为清晰的表格
            period1_table = self._format_data_to_table(period1_data, "时段一")
            period2_table = self._format_data_to_table(period2_data, "时段二")
            
            # 4. 构建全新的结构化Master Prompt
            # ------------------- 全新的、结构化的Master Prompt -------------------
            master_prompt = f"""
# 角色
你是一位顶级的餐厅财务数据分析师和商业顾问，你的客户是"美莲花餐厅"的老板。你的分析风格必须：**数据驱动、逻辑严谨、建议具体、格式清晰**。

# 任务
请根据以下两个时间段的支出汇总数据，为餐厅老板生成一份专业的、深入的财务对比分析报告。

# 原始数据
## 时段一: {period1_dates[0]} 至 {period1_dates[1]}
{period1_table}

## 时段二: {period2_dates[0]} 至 {period2_dates[1]}
{period2_table}

# 报告生成要求
请严格按照以下 **四个部分** 的结构来生成你的报告，并使用 **Markdown** 格式化文本，确保报告的专业性和可读性。

---
### **【第一部分：总体财务概览】**
请在报告的最开始，用简洁的语言和关键数据总结两个时段的总体支出变化。必须包含：
- 两个时段的**总支出**。
- 支出的**绝对差额**。
- 支出的**变化率（%）**。
- 基于变化率给出一个简短的、定性的初步结论（例如："支出规模基本稳定"、"出现显著增长，需重点关注"）。

---
### **【第二部分：核心数据对比表】**
这是报告的核心。请创建一个Markdown表格，清晰地对比两个时段内 **每一个支出品类** 的数据。表格必须包含以下列：`支出分类`, `时段一金额(元)`, `时段二金额(元)`, `差额(元)`, `变化率(%)`。请对差额和变化率进行精确计算。如果某个品类只在一个时段出现，也要在表格中明确体现出来。

---
### **【第三部分：关键品类深度分析】**
请基于你生成的上述表格，**挑选出2-3个最值得关注的变化品类**进行深度分析。分析应聚焦于：
- **金额变动最大**: 哪个品类的支出金额增加或减少最多？这个变动占总体差额的百分之多少？
- **比率变动最剧烈**: 哪个品类的支出百分比变化最大？这反映了什么潜在问题？
- **新增或消失的大额项目**: 是否有新的大额支出项出现，或旧的大额支出项消失？它们可能代表了什么经营活动？

---
### **【第四部分：经营诊断与行动建议】**
这是展现你专业价值的部分。基于前面的数据和分析，请提供具体、可落地的建议。建议必须分为两类，且必须是**向老板提出的、可供他直接执行或调查的问题**：
1.  **【🔍 需要您立即核实的问题】**: 提出需要老板去亲自调查的疑点。例如："'清洁用品'支出异常增长了3900%。**请您立刻核实**：这期间是否存在大批量囤货、采购单价上涨或数据录入错误的情况？请检查编号XXX到XXX的采购发票。"
2.  **【💡 可考虑的行动方案】**: 提出具体的、前瞻性的改进建议。例如："肉类成本是总支出的主要部分且呈上涨趋势。**建议**：1. 本周内与主要肉类供应商安排一次会议，就采购量问题进行一次价格谈判。2. 请厨师长评估，是否可以通过调整2-3款核心肉类菜品的份量或配菜组合，在不影响顾客体验的前提下优化成本结构。"
"""
            # ------------------- Master Prompt 结束 -------------------

            # 5. 调用DeepSeek API（带重试机制）
            max_retries = 2
            retry_count = 0
            
            while retry_count <= max_retries:
                try:
                    response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[
                            {
                                "role": "user", 
                                "content": master_prompt
                            }
                        ],
                        temperature=0.7,  # 适中的创造性，保证分析的专业性和多样性
                        max_tokens=4000,  # 确保有足够的token生成完整报告
                        stream=False
                    )
                    break  # 成功则跳出重试循环
                    
                except Exception as api_error:
                    retry_count += 1
                    error_msg = str(api_error).lower()
                    
                    # 如果是超时错误且还有重试次数，则重试
                    if ("timeout" in error_msg or "timed out" in error_msg) and retry_count <= max_retries:
                        # 发送重试提示（可选）
                        continue
                    else:
                        # 重新抛出异常，让外层catch处理
                        raise api_error
            
            # 6. 检查并发射成功信号
            if response.choices and len(response.choices) > 0:
                analysis_report = response.choices[0].message.content
                if analysis_report:
                    self.finished.emit(analysis_report)
                else:
                    self.error.emit("❌ 错误：AI模型返回了空的响应，请稍后重试。")
            else:
                self.error.emit("❌ 错误：AI模型未返回有效响应，请稍后重试。")
        
        except Exception as e:
            # 捕获所有可能的错误并发射错误信号
            error_msg = str(e)
            
            # 根据不同类型的错误提供针对性的错误信息
            if "api_key" in error_msg.lower():
                error_message = f"❌ API密钥错误：{error_msg}\n请检查config.ini中的DEEPSEEK_API_KEY配置。"
            elif "network" in error_msg.lower() or "connection" in error_msg.lower():
                error_message = f"❌ 网络连接错误：{error_msg}\n请检查网络连接并稍后重试。"
            elif "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                error_message = f"❌ 请求超时：AI分析耗时较长，已超过90秒限制\n\n💡 解决方案：\n1. 您的API调用已成功，token已消耗（这是正常的）\n2. 请稍等1-2分钟后重试，避免重复计费\n3. 可以尝试缩小时间范围以减少数据量\n4. 网络较慢时建议在网络状况良好时重试\n\n🔧 技术详情：{error_msg}"
            elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
                error_message = f"❌ API配额限制：{error_msg}\n请检查您的DeepSeek API使用配额。"
            elif "unauthorized" in error_msg.lower() or "401" in error_msg:
                error_message = f"❌ 认证失败：API密钥无效或已过期\n请更新config.ini中的DEEPSEEK_API_KEY。"
            elif "forbidden" in error_msg.lower() or "403" in error_msg:
                error_message = f"❌ 访问被拒绝：API密钥权限不足\n请检查您的DeepSeek账户权限。"
            else:
                error_message = f"❌ AI分析服务暂时不可用：{error_msg}\n请稍后重试或联系技术支持。"
            
            self.error.emit(error_message)
    
    def _format_data_to_table(self, data, period_name):
        """
        将支出数据格式化为清晰的表格字符串
        
        Args:
            data (list): 支出数据列表
            period_name (str): 时段名称
        
        Returns:
            str: 格式化的表格字符串
        """
        if not data:
            return f"{period_name}：无支出记录"
        
        # 计算总支出
        total_amount = sum(item.get('total_amount', 0) for item in data)
        
        # 构建表格
        table_lines = [
            f"{period_name}支出明细:",
            "┌─────────────────────┬──────────────────┬─────────┐",
            "│ 支出分类            │ 金额(元)         │ 占比(%) │",
            "├─────────────────────┼──────────────────┼─────────┤"
        ]
        
        # 按金额排序
        sorted_data = sorted(data, key=lambda x: x.get('total_amount', 0), reverse=True)
        
        for item in sorted_data:
            category = item.get('category_cn', '未知分类')
            amount = item.get('total_amount', 0)
            percentage = (amount / total_amount * 100) if total_amount > 0 else 0
            
            # 格式化行
            category_padded = f"{category:<10}"[:10].ljust(10)
            amount_formatted = f"¥{amount:,.2f}".rjust(15)
            percentage_formatted = f"{percentage:.1f}%".rjust(6)
            
            table_lines.append(f"│ {category_padded}        │ {amount_formatted} │ {percentage_formatted} │")
        
        table_lines.extend([
            "├─────────────────────┼──────────────────┼─────────┤",
            f"│ 合计                │ ¥{total_amount:,.2f}".ljust(39) + "│ 100.0%  │",
            "└─────────────────────┴──────────────────┴─────────┘"
        ])
        
        return "\n".join(table_lines)


class ConnectionTestWorker(QObject):
    """
    连接测试Worker类 - 在后台线程中测试DeepSeek API连接
    
    用于在不阻塞UI的情况下测试API连接状态
    """
    
    # 定义信号
    finished = pyqtSignal(bool, str)  # 测试完成时发射，携带(是否成功, 结果信息)
    
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
    
    def run_test(self):
        """
        在后台线程中执行连接测试
        """
        try:
            # 加载配置
            config = configparser.ConfigParser()
            # 保持选项名大小写
            config.optionxform = str
            config_path = self.get_config_path()
            
            if not os.path.exists(config_path):
                self.finished.emit(False, "未找到config.ini配置文件")
                return
            
            config.read(config_path, encoding='utf-8')
            
            # 获取API密钥
            api_key = None
            if config.has_section('DEEPSEEK'):
                if config.has_option('DEEPSEEK', 'API_KEY'):
                    api_key = config.get('DEEPSEEK', 'API_KEY').strip()
                elif config.has_option('DEEPSEEK', 'api_key'):
                    api_key = config.get('DEEPSEEK', 'api_key').strip()
            elif config.has_section('API') and config.has_option('API', 'DEEPSEEK_API_KEY'):
                api_key = config.get('API', 'DEEPSEEK_API_KEY').strip()
            
            if not api_key or api_key == 'sk-':
                self.finished.emit(False, "未配置DEEPSEEK_API_KEY")
                return
            
            # 初始化客户端
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com/v1",
                timeout=10.0  # 测试连接时使用较短的超时时间
            )
            
            # 发送测试请求
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": "请回复：连接测试成功"}],
                max_tokens=50
            )
            
            if response.choices and len(response.choices) > 0:
                self.finished.emit(True, f"连接成功: {response.choices[0].message.content}")
            else:
                self.finished.emit(False, "API响应异常")
                
        except Exception as e:
            self.finished.emit(False, f"连接失败: {str(e)}")



