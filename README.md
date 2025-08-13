# 美莲花餐厅支出记录系统

## نىلۇپار ئاشخانا چىقىم خاتىرىسى سىستېمىسى

一个专为美莲花餐厅设计的现代化支出记录管理系统，采用双语界面（中文/维语）和Fluent Design设计风格。初始管理员用户名：Admin；初始管理员密码：000000.
[![下载安装包](https://img.shields.io/badge/下载安装包-Download-brightgreen?style=for-the-badge)](https://github.com/narmi924/Nilufar_Restaurant_System/releases/download/v2.0/Nilufar_Restaurant_System_Setup.exe)

## 系统概述

这是一个完整的餐厅财务管理系统，包含用户管理、支出录入、报表分析、数据查询等核心功能。系统采用PyQt6框架开发，使用SQLite数据库存储数据，支持数据导出和双时段对比分析。

## 技术架构

### 开发环境

- **开发语言**: Python 3.7+
- **UI框架**: PyQt6 + PyQt-Fluent-Widgets
- **数据库**: SQLite 3
- **数据分析**: pandas, matplotlib, numpy
- **文档生成**: openpyxl

### 依赖包

```txt
PyQt6>=6.4.0
pandas>=1.5.0
matplotlib>=3.6.0
numpy>=1.21.0
openpyxl>=3.0.0
openai>=1.0.0
PyQt-Fluent-Widgets>=1.4.0
```

## 项目结构

```text
Nilufar_Restaurant_System/
├── app.py                      # 主程序入口
├── models.py                   # 数据模型和数据库操作
├── database.py                 # 数据库连接和初始化
├── login_window.py             # 登录窗口
├── main_window.py              # 主界面（支出录入）
├── reporting_page.py           # 报表中心页面（集成AI分析）
├── query_window.py             # 查询窗口
├── analysis_engine.py          # 数据分析引擎
├── workers.py                  # AI分析多线程工作器
├── expense_input_dialog.py     # 支出输入对话框
├── user_profile_dialog.py      # 用户配置对话框
├── daily_records_window.py     # 日常记录窗口
├── config.ini                  # 配置文件（DeepSeek API设置）
├── restaurant.db               # SQLite数据库文件
├── requirements.txt            # 依赖包列表
├── run.py                      # 快速启动脚本
└── my_icon.ico                 # 应用程序图标

```

## 核心模块详解

### 1. 主程序入口 (app.py)

**功能**: 应用程序的主控制器，管理窗口间的跳转和生命周期

**关键类**:

- `RestaurantApp`: 主应用程序类
  - `run()`: 启动应用程序，显示登录窗口
  - `show_login_window()`: 创建和显示登录界面
  - `on_login_successful()`: 处理登录成功事件，跳转到主窗口
  - `show_main_window()`: 创建和显示主操作界面
  - `show_reporting_window()`: 打开报表分析窗口
  - `show_query_window()`: 打开查询窗口

**页面跳转关系**:

- 登录页面 → 主界面
- 主界面 → 报表中心/查询窗口/设置窗口

### 2. 数据模型层 (models.py)

**功能**: 定义所有数据库操作和业务逻辑

**核心函数**:

- `verify_user(username, password)`: 用户身份验证，支持密码加密
- `add_expense(date, amount, category_id, user_id, notes)`: 添加支出记录
- `get_expenses_by_date_range(start_date, end_date, category_id)`: 按日期范围查询支出
- `get_all_categories()`: 获取所有支出分类
- `get_total_expenses_by_category(start_date, end_date)`: 按分类统计支出总额
- `update_expense(expense_id, amount, notes)`: 更新支出记录
- `delete_expense(expense_id)`: 删除支出记录
- `add_category(name_cn, name_ug)`: 添加新分类
- `update_user_credentials()`: 更新用户密码

### 3. 数据库层 (database.py)

**功能**: 管理数据库连接、表结构初始化和权限检查

**核心函数**:

- `create_connection()`: 创建数据库连接，支持开发/生产环境
- `create_tables()`: 创建数据库表结构
- `initialize_database()`: 初始化数据库，插入默认数据
- `check_database_permissions()`: 检查数据库文件权限

**数据库结构**:

- `users`: 用户表 (id, username, password, role)
- `categories`: 分类表 (id, name_cn, name_ug)
- `expenses`: 支出记录表 (id, expense_date, amount, category_id, user_id, notes)

### 4. 登录窗口 (login_window.py)

**功能**: 用户身份验证界面，采用Fluent Design风格

**核心类**:

- `LoginWindow`: 登录窗口主类
  - `init_ui()`: 初始化双语界面布局
  - `create_header_area()`: 创建标题区域
  - `create_input_area()`: 创建用户名和密码输入区域
  - `create_button_area()`: 创建登录按钮区域
  - `handle_login()`: 处理登录验证逻辑

**界面特色**:

- 双语标题显示（中文/维语）
- 使用InfoBar替代传统MessageBox
- 记忆上次登录用户名
- 支持回车键快速登录

### 5. 主操作界面 (main_window.py)

**功能**: 系统核心界面，支出录入和导航中心

**核心类**:

- `MainWindow`: 继承自FluentWindow的主窗口
  - `init_ui()`: 初始化界面布局
  - `create_category_buttons_area()`: 创建分类按钮网格
  - `load_categories()`: 从数据库加载分类数据
  - `select_category()`: 处理分类选择
  - `open_expense_input_dialog()`: 打开支出输入对话框

**界面布局**:

- 系统标题区域（双语显示）
- 用户信息和日期选择区域
- 分类按钮网格区域（可滚动）
- 功能按钮区域（编辑记录、报表中心、查询、设置）

### 6. 报表中心 (reporting_page.py)

**功能**: 财务数据分析和AI智能报表生成

**核心类**:

- `ReportingPage`: 报表分析页面
  - `create_header_section()`: 创建查询条件区域
  - `create_single_analysis_widget()`: 单时段分析控件
  - `create_compare_analysis_widget()`: 双时段对比控件
  - `generate_single_report()`: 生成单时段报表
  - `generate_compare_report()`: 生成双时段对比报表（集成AI分析）
  - `on_ai_analysis_finished()`: AI分析完成处理
  - `export_report()`: 导出Excel报表

**分析功能**:

- 单时段分析：指定日期范围和分类的支出统计
- 双时段对比：两个时间段的支出对比分析
- **AI智能分析**：DeepSeek AI驱动的深度财务分析
- **Markdown富文本显示**：美观的报告格式化显示
- 数据可视化表格显示
- Excel导出功能

### 6.1. AI分析工作器 (workers.py)

**功能**: 多线程AI分析处理，避免UI阻塞

**核心类**:

- `AIAnalysisWorker`: AI分析工作线程
  - `run_analysis()`: 执行DeepSeek API调用和数据分析
  - `_format_data_to_table()`: 格式化数据为分析表格
  - 信号：`finished`, `error`
- `ConnectionTestWorker`: API连接测试工作线程

**技术特性**:

- 非阻塞UI设计，保持界面响应性
- 90秒超时设置，支持2次重试机制
- 专业的餐厅财务分析提示词工程
- 完整的错误处理和用户反馈

### 7. 查询窗口 (query_window.py)

**功能**: 支出记录查询和数据导出

**核心类**:

- `QueryWindow`: 查询窗口主类
  - `create_query_conditions_area()`: 创建筛选条件区域
  - `create_summary_area()`: 创建统计信息显示区域
  - `create_table_area()`: 创建结果表格区域
  - `handle_query()`: 执行查询操作
  - `update_table()`: 更新表格数据显示
  - `handle_export()`: 导出查询结果到Excel

**查询功能**:

- 按日期范围筛选
- 按支出分类筛选
- 实时统计总记录数、总金额、平均金额
- 支持数据排序和Excel导出

### 8. 数据分析引擎 (analysis_engine.py)

**功能**: 生成智能化的财务分析报告

**核心函数**:

- `generate_comparison_report()`: 生成双时段对比分析报告
  - 计算总支出变化率
  - 分析各分类支出变化
  - 识别显著异动项目
  - 生成经营建议

**分析维度**:

- 总体支出对比
- 详细品类对比
- 核心品类异动分析
- 经营诊断与建议

### 9. 支出输入对话框 (expense_input_dialog.py)

**功能**: 二次确认支出录入的模态对话框

**核心类**:

- `ExpenseInputDialog`: 支出输入对话框
  - `create_header_area()`: 显示选择的分类和日期
  - `create_input_area()`: 金额和备注输入区域
  - `handle_save()`: 保存支出记录到数据库

**输入验证**:

- 金额格式验证（最多两位小数）
- 必填字段检查
- 数据库操作异常处理

### 10. 其他辅助模块

**user_profile_dialog.py**: 用户配置对话框

- 密码修改功能
- 用户信息管理

**daily_records_window.py**: 日常记录管理窗口

- 当日记录查看和编辑
- 记录删除功能

## 数据库设计

### 表结构

#### users (用户表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PRIMARY KEY | 用户ID |
| username | TEXT NOT NULL UNIQUE | 用户名 |
| password | TEXT NOT NULL | 密码（SHA256加密） |
| role | TEXT NOT NULL | 用户角色 |

#### categories (分类表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PRIMARY KEY | 分类ID |
| name_cn | TEXT NOT NULL UNIQUE | 中文名称 |
| name_ug | TEXT NOT NULL UNIQUE | 维语名称 |

#### expenses (支出记录表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PRIMARY KEY | 记录ID |
| expense_date | TEXT NOT NULL | 支出日期 |
| amount | REAL NOT NULL | 支出金额 |
| category_id | INTEGER | 分类ID（外键） |
| user_id | INTEGER | 用户ID（外键） |
| notes | TEXT | 备注信息 |

### 初始数据

系统会自动插入以下初始数据：

**默认用户**:

- 用户名: admin
- 密码: 123456
- 角色: admin

**默认分类**:

- 羊肉 / قوي گۆشى
- 牛肉 / كالا گۆشى
- 鸡肉 / توخۇ گۆشى
- 鱼肉 / بېلىق گۆشى
- 蔬菜 / كۆكتات
- 调料 / تېتىتقۇ
- 酸奶 / قېتىق
- 牛肚 / قېرېن
- 羊肉串 / كاۋاپ
- 油塔子 / يۇتازا
- 清洁用品 / تازلىق بۇيۇملىرى

## 系统特色功能

### 1. 双语界面支持

- 中文和维吾尔语双语显示
- 界面元素、按钮、提示信息均支持双语
- 数据库分类名称双语存储

### 2. Fluent Design界面

- 采用Microsoft Fluent Design设计语言
- 现代化的卡片式布局
- 流畅的动画效果和交互体验
- InfoBar替代传统消息框

### 3. AI智能数据分析

- **DeepSeek AI集成**：专业的餐厅财务分析AI
- **双时段对比分析**：智能识别支出变化趋势
- **深度经营诊断**：AI生成具体的经营建议和行动计划
- **异常预警系统**：自动识别异常支出变化
- **Markdown富文本报告**：美观的格式化分析报告
- **多线程处理**：AI分析过程中界面保持响应

### 4. 灵活的数据导出

- Excel格式导出
- 自定义查询条件
- 完整的报表数据导出

### 5. 用户权限管理

- 用户角色区分
- 密码加密存储
- 登录状态管理
- **AI功能权限控制**：仅管理员可使用AI分析功能

## 安装和运行

### 环境要求

- Python 3.7 或更高版本
- Windows 10 或更高版本（推荐）

### 安装步骤

1. **克隆项目**

```bash
git clone https://github.com/narmi924/Nilufar_Restaurant_System
cd Nilufar_Restaurant_System
```

1. **安装依赖**

```bash
pip install -r requirements.txt
```

1. **配置DeepSeek API（可选）**

```ini
在设置中的API配置页面中输入自己的DeepSeek API密钥
```

1. **运行系统**

下载安装包安装后直接运行exe文件

或者
```bash
# 正确目录下在终端运行：
python app.py

# 或者运行：
PyInstaller --noconsole --onefile --icon="my_icon.ico" --add-data "restaurant.db;." --add-data "sounds;sounds" --name "美莲花餐厅系统" app.py
# 来打包生成exe文件并运行
```


### 首次使用

1. 系统启动后会自动创建数据库和初始数据
2. 使用默认账户登录：
   - 用户名: admin
   - 密码: 000000
3. 登录后可以开始录入支出数据

## 使用指南

### 基本操作流程

1. **登录系统**
   - 输入用户名和密码
   - 点击登录按钮

2. **录入支出**
   - 选择支出日期
   - 点击对应的分类按钮
   - 在弹出对话框中输入金额和备注
   - 点击保存

3. **查看报表**
   - 点击"报表中心"按钮
   - 选择分析模式（单时段/双时段对比）
   - 设置查询条件
   - 点击"生成报表"
   - **AI智能分析**（仅管理员）：双时段对比模式下自动生成AI分析报告

4. **查询数据**
   - 点击"查询"按钮
   - 设置筛选条件
   - 查看查询结果
   - 可导出为Excel文件

5. **日常管理**
   - 点击"编辑今日记录"查看和修改当日记录
   - 在设置中可以修改密码和管理分类

### 快捷键支持

- **登录界面**: 回车键快速登录
- **支出输入**: 回车键保存记录
- **退出**: ESC键关闭当前窗口

## 常见问题

### Q: 数据库文件在哪里？

A: 数据库文件`restaurant.db`位于程序根目录下，包含所有的用户数据和支出记录。

### Q: 如何备份数据？

A: 复制`restaurant.db`文件即可备份所有数据。恢复时将备份文件覆盖即可。

### Q: 忘记密码怎么办？

A: 可以删除数据库文件，系统将重建数据库并恢复默认账户（admin/123456）。

### Q: 如何添加新的支出分类？

A: 在主界面点击"设置"按钮，可以添加、修改、删除支出分类。

### Q: 支持多用户同时使用吗？

A: 系统设计为单用户使用，不支持多用户同时操作同一数据库。

### Q: AI分析功能如何使用？

A:

1. 需要使用管理员账户（admin）登录
2. 设置中配置DeepSeek API密钥
3. 在报表中心选择"双时段对比"模式
4. 设置两个时间段后点击"生成对比"
5. 系统将自动调用AI进行深度分析

### Q: AI分析超时怎么办？

A:

- AI分析设置了90秒超时，复杂分析需要更多时间
- 系统会自动重试2次
- 即使超时，API调用仍然有效，可稍后重试
- 确保网络连接稳定

### Q: 为什么看不到AI分析功能？

A: AI分析功能仅限管理员使用，需要：

1. 使用admin账户登录
2. 在双时段对比模式下才会显示AI分析结果
3. 确保已正确配置DeepSeek API密钥

## 系统架构图

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   登录界面      │───→│   主操作界面    │───→│   报表中心      │
│ LoginWindow     │    │  MainWindow     │    │ ReportingPage   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌────────┼────────┐
                       ▼        ▼        ▼
            ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
            │  查询窗口   │ │  设置窗口   │ │  记录编辑   │
            │QueryWindow  │ │UserProfile  │ │DailyRecords │
            └─────────────┘ └─────────────┘ └─────────────┘
                       │
                       ▼
            ┌─────────────────────────────────┐
            │         数据访问层              │
            │  models.py + database.py        │
            └─────────────────────────────────┘
                       │
                       ▼
            ┌─────────────────────────────────┐
            │       SQLite数据库              │
            │      restaurant.db              │
            └─────────────────────────────────┘
```

## 维护和扩展

### 代码结构说明

- 采用MVC架构模式
- 界面与业务逻辑分离
- 数据访问层统一管理
- 支持模块化扩展

### 扩展建议

1. 可以添加更多的AI分析模型和提示词
2. 支持网络数据库（MySQL/PostgreSQL）
3. 添加数据自动备份功能
4. 支持更多的导出格式（PDF、图表等）
5. 添加用户权限细分管理
6. 集成更多AI服务提供商（OpenAI、Claude等）
7. 添加语音输入和语音播报功能

## 技术支持

如有技术问题或功能建议，请联系Imranjan Mamtimin。

---

## 更新日志

**当前版本**: v2.0
**开发**: Imranjan Mamtimin
**更新日期**: 2025年8月8日




