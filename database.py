import sqlite3
import os
import sys
import pathlib
import shutil


def get_resource_path(relative_path):
    """ 获取资源的绝对路径，兼容开发环境和PyInstaller打包环境 """
    try:
        # PyInstaller创建的临时文件夹，並将路径存在 _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # 开发环境中，直接使用当前文件的路径
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


# 定义持久化的应用数据目录
APP_NAME = "MeilianhuaRestaurantSystem"
APP_DATA_DIR = pathlib.Path.home() / 'AppData' / 'Roaming' / APP_NAME
DB_PATH = APP_DATA_DIR / "restaurant.db"

# 确保应用数据目录存在
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)


def check_database_permissions(db_path):
    """
    检查数据库文件的读写权限
    
    Args:
        db_path (pathlib.Path): 数据库文件路径
        
    Returns:
        tuple: (can_read: bool, can_write: bool, error_message: str)
    """
    try:
        # 检查目录是否存在
        db_dir = db_path.parent
        if not db_dir.exists():
            return False, False, f"数据库目录不存在: {db_dir}"
        
        # 检查目录写权限
        if not os.access(str(db_dir), os.W_OK):
            return False, False, f"数据库目录无写权限: {db_dir}"
        
        # 如果数据库文件存在，检查文件权限
        if db_path.exists():
            can_read = os.access(str(db_path), os.R_OK)
            can_write = os.access(str(db_path), os.W_OK)
            
            if not can_read:
                return False, False, f"数据库文件无读权限: {db_path}"
            if not can_write:
                return False, False, f"数据库文件无写权限: {db_path}"
            
            return True, True, "权限检查通过"
        else:
            # 文件不存在，检查是否可以创建
            try:
                # 尝试创建一个临时文件来检查写权限
                temp_file = db_dir / 'temp_permission_check.tmp'
                temp_file.write_text('permission_check')
                temp_file.unlink()
                return True, True, "权限检查通过（数据库文件将被创建）"
            except Exception as e:
                return False, False, f"无法在目录中创建文件: {str(e)}"
                
    except Exception as e:
        return False, False, f"权限检查时发生错误: {str(e)}"


def create_connection():
    """
    创建数据库连接
    连接到用户专属应用数据目录中的 restaurant.db 数据库
    增强版：智能处理路径和权限问题
    
    Returns:
        sqlite3.Connection: 数据库连接对象
    """
    try:
        # 检查权限
        can_read, can_write, perm_message = check_database_permissions(DB_PATH)
        
        if not can_write:
            raise Exception(f"数据库写权限不足: {perm_message}")
        
        # 创建数据库连接
        conn = sqlite3.connect(str(DB_PATH))
        
        # 设置一些有用的SQLite选项
        conn.execute("PRAGMA journal_mode=WAL")  # 启用WAL模式，提高并发性能
        conn.execute("PRAGMA synchronous=NORMAL")  # 平衡性能和数据安全
        conn.execute("PRAGMA temp_store=MEMORY")  # 临时表存储在内存中
        conn.execute("PRAGMA cache_size=10000")  # 增加缓存大小
        
        return conn
        
    except sqlite3.Error as e:

        return None
    except Exception as e:

        return None


def create_tables(conn):
    """
    创建数据库表结构
    
    Args:
        conn: 数据库连接对象
    """
    try:
        cursor = conn.cursor()
        
        # 创建用户表
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        );
        """
        
        # 创建支出分类表
        create_categories_table = """
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_cn TEXT NOT NULL UNIQUE,
            name_ug TEXT NOT NULL UNIQUE,
            emoji TEXT DEFAULT '📝'
        );
        """
        
        # 创建支出记录表
        create_expenses_table = """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_date TEXT NOT NULL,
            amount REAL NOT NULL,
            category_id INTEGER,
            user_id INTEGER,
            notes TEXT,
            FOREIGN KEY (category_id) REFERENCES categories (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        """
        
        # 执行创建表的SQL语句
        cursor.execute(create_users_table)
        cursor.execute(create_categories_table)
        cursor.execute(create_expenses_table)
        
        # 检查是否需要为现有的categories表添加emoji字段
        cursor.execute("PRAGMA table_info(categories)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if 'emoji' not in column_names:
            # 添加emoji字段并设置默认值
            cursor.execute("ALTER TABLE categories ADD COLUMN emoji TEXT DEFAULT '📝'")
            
            # 为现有分类设置默认表情
            default_emojis = {
                '羊肉': '🐑', '牛肉': '🐄', '鸡肉': '🐔', '鱼肉': '🐟',
                '蔬菜孙玲': '🥬', '蔬菜巴克': '🥒', '调料': '🧂', 
                '酸奶': '🥛', '牛肚': '🫃', '羊肉串': '🍢', 
                '油塔子': '🫒', '清洁用品': '🧽'
            }
            
            for name_cn, emoji in default_emojis.items():
                cursor.execute(
                    "UPDATE categories SET emoji = ? WHERE name_cn = ?", 
                    (emoji, name_cn)
                )
        
        conn.commit()
        
    except sqlite3.Error as e:

        pass


def insert_initial_data(conn):
    """
    插入初始数据到数据库
    
    Args:
        conn: 数据库连接对象
    """
    try:
        from models import hash_password  # 导入密码哈希函数
        cursor = conn.cursor()
        
        # 检查用户表是否为空，如果为空则插入默认管理员账户
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            # 插入默认管理员账户，密码需要哈希处理
            hashed_password = hash_password('123456')
            cursor.execute("""
                INSERT INTO users (username, password, role) 
                VALUES (?, ?, ?)
            """, ('admin', hashed_password, 'admin'))
        
        # 检查分类表是否为空，如果为空则插入初始分类
        cursor.execute("SELECT COUNT(*) FROM categories")
        category_count = cursor.fetchone()[0]
        
        if category_count == 0:
            # 初始分类数据
            initial_categories = [
                ('羊肉', 'قوي گۆشى'),
                ('牛肉', 'كالا گۆشى'),
                ('鸡肉', 'توخۇ گۆشى'),
                ('鱼肉', 'بېلىق گۆشى'),
                ('蔬菜孙玲', 'كۆكتات سۇنلىڭ'),
                ('蔬菜巴克', 'كۆكتات باقى'),
                ('调料', 'تېتىتقۇ'),
                ('酸奶', 'قېتىق'),
                ('牛肚', 'قېرېن'),
                ('羊肉串', 'كاۋاپ'),
                ('油塔子', 'يۇتازا'),
                ('清洁用品', 'تازلىق بۇيۇملىرى')
            ]
            
            # 插入初始分类数据
            cursor.executemany("""
                INSERT INTO categories (name_cn, name_ug) 
                VALUES (?, ?)
            """, initial_categories)
        
        # 提交所有更改
        conn.commit()
        
    except sqlite3.Error as e:

        conn.rollback()


def initialize_database():
    """
    初始化数据库 - 智能首次运行安装数据库
    实现"首次运行安装数据库"的能力，支持从打包资源复制种子数据库
    
    Returns:
        bool: 初始化是否成功
    """
    try:
        # 检查最终的数据库路径是否存在
        if not DB_PATH.exists():
    
            
            # 尝试从打包资源中复制种子数据库
            try:
                source_db_path = get_resource_path('restaurant.db')
                if os.path.exists(source_db_path):
        
                    shutil.copy(source_db_path, DB_PATH)

                    return True
                else:

                    # 继续执行创建新数据库的逻辑
                    pass
            except Exception as e:

                # 继续执行创建新数据库的逻辑
                pass
            
            # 创建全新的空数据库
            conn = create_connection()
            if conn is None:
    
                return False
            
            try:
                # 创建表结构
                create_tables(conn)
    
                
                # 插入初始数据
                insert_initial_data(conn)
    
                
    
                return True
                
            except Exception as e:
        
                conn.rollback()
                return False
            
            finally:
                conn.close()
        
        else:
            # 数据库已存在，跳过初始化
    
            return True
            
    except Exception as e:

        return False


