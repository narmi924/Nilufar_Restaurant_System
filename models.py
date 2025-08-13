import hashlib
import sqlite3
from database import create_connection


def hash_password(password):
    """
    使用SHA256算法对密码进行哈希加密
    
    Args:
        password (str): 明文密码
        
    Returns:
        str: 加密后的十六进制字符串
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def verify_user(username, password):
    """
    验证用户名和密码是否正确
    
    Args:
        username (str): 用户名
        password (str): 用户输入的明文密码
        
    Returns:
        str or None: 如果验证成功返回用户角色，失败返回None
    """
    conn = None
    try:
        # 加密用户输入的密码
        hashed_password = hash_password(password)
        
        # 连接数据库
        conn = create_connection()
        if conn is None:
            return None
            
        cursor = conn.cursor()
        
        # 查询用户信息
        cursor.execute("""
            SELECT password, role FROM users WHERE username = ?
        """, (username,))
        
        result = cursor.fetchone()
        
        if result is None:
            return None
            
        stored_password, role = result
        
        # 兼容性处理：如果存储的是明文密码，先加密再比较
        # 如果长度不是64位（SHA256的十六进制长度），说明是明文密码
        if len(stored_password) != 64:
            # 更新数据库中的密码为加密版本
            encrypted_stored_password = hash_password(stored_password)
            cursor.execute("""
                UPDATE users SET password = ? WHERE username = ?
            """, (encrypted_stored_password, username))
            conn.commit()
            stored_password = encrypted_stored_password
        
        # 比较密码
        if stored_password == hashed_password:
            return role
        else:
            return None
            
    except sqlite3.Error as e:
        # 数据库错误保留日志

        return None
    except Exception as e:
        # 系统错误保留日志

        return None
    finally:
        if conn:
            conn.close()


def add_expense(expense_date, amount, category_id, user_id, notes=""):
    """
    向数据库中添加一条新的支出记录
    
    Args:
        expense_date (str): 支出日期 (YYYY-MM-DD格式)
        amount (float): 支出金额
        category_id (int): 分类ID
        user_id (int): 操作员用户ID
        notes (str): 备注信息，可选
        
    Returns:
        bool: 成功返回True，失败返回False
    """
    conn = None
    try:
        conn = create_connection()
        if conn is None:
            return False
            
        cursor = conn.cursor()
        
        # 计算当天该分类的下一个序号
        cursor.execute("""
            SELECT COALESCE(MAX(sequence_number), 0) + 1
            FROM expenses 
            WHERE expense_date = ? AND category_id = ?
        """, (expense_date, category_id))
        
        next_sequence = cursor.fetchone()[0]
        
        # 插入支出记录
        cursor.execute("""
            INSERT INTO expenses (expense_date, amount, category_id, user_id, notes, sequence_number)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (expense_date, amount, category_id, user_id, notes, next_sequence))
        
        conn.commit()
        return True
        
    except sqlite3.Error as e:

        return False
    except Exception as e:

        return False
    finally:
        if conn:
            conn.close()


def get_all_categories():
    """
    获取所有的支出分类
    
    Returns:
        list: 包含所有分类信息的字典列表，每个字典包含id, name_cn, name_ug, emoji
    """
    conn = None
    try:
        conn = create_connection()
        if conn is None:
            return []
            
        cursor = conn.cursor()
        
        # 查询所有分类
        cursor.execute("""
            SELECT id, name_cn, name_ug, emoji FROM categories ORDER BY id
        """)
        
        results = cursor.fetchall()
        
        # 转换为字典列表
        categories = []
        for row in results:
            categories.append({
                'id': row[0],
                'name_cn': row[1],
                'name_ug': row[2],
                'emoji': row[3] if row[3] else '📝'  # 默认表情
            })
            
        return categories
        
    except sqlite3.Error as e:

        return []
    except Exception as e:

        return []
    finally:
        if conn:
            conn.close()


def get_expenses_by_date_range(start_date, end_date, category_id=None):
    """
    根据日期范围和可选的分类来查询支出明细
    
    Args:
        start_date (str): 开始日期 (YYYY-MM-DD格式)
        end_date (str): 结束日期 (YYYY-MM-DD格式)
        category_id (int, optional): 分类ID，如果提供则只查询该分类的支出
        
    Returns:
        list: 查询结果列表，每项包含 (日期, 分类名, 金额, 用户名, 备注)
    """
    conn = None
    try:
        conn = create_connection()
        if conn is None:
            return []
            
        cursor = conn.cursor()
        
        # 构建查询SQL
        if category_id is not None:
            # 查询特定分类的支出
            sql = """
                SELECT 
                    e.expense_date,
                    c.name_cn,
                    e.amount,
                    u.username,
                    e.notes
                FROM expenses e
                JOIN categories c ON e.category_id = c.id
                JOIN users u ON e.user_id = u.id
                WHERE e.expense_date >= ? AND e.expense_date <= ?
                AND e.category_id = ?
                ORDER BY e.expense_date DESC, e.id DESC
            """
            cursor.execute(sql, (start_date, end_date, category_id))
        else:
            # 查询所有分类的支出
            sql = """
                SELECT 
                    e.expense_date,
                    c.name_cn,
                    e.amount,
                    u.username,
                    e.notes
                FROM expenses e
                JOIN categories c ON e.category_id = c.id
                JOIN users u ON e.user_id = u.id
                WHERE e.expense_date >= ? AND e.expense_date <= ?
                ORDER BY e.expense_date DESC, e.id DESC
            """
            cursor.execute(sql, (start_date, end_date))
        
        results = cursor.fetchall()
        return results
        
    except sqlite3.Error as e:

        return []
    except Exception as e:

        return []
    finally:
        if conn:
            conn.close()


def get_user_id_by_username(username):
    """
    根据用户名获取用户ID
    
    Args:
        username (str): 用户名
        
    Returns:
        int or None: 用户ID，如果用户不存在则返回None
    """
    conn = None
    try:
        conn = create_connection()
        if conn is None:
            return None
            
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        return result[0] if result else None
        
    except sqlite3.Error as e:

        return None
    except Exception as e:

        return None
    finally:
        if conn:
            conn.close()


def get_total_expenses_by_category(start_date, end_date):
    """
    按分类统计指定日期范围内的支出总额
    
    Args:
        start_date (str): 开始日期 (YYYY-MM-DD格式)
        end_date (str): 结束日期 (YYYY-MM-DD格式)
        
    Returns:
        list: 包含分类统计信息的字典列表，每个字典包含category_name, total_amount
    """
    conn = None
    try:
        conn = create_connection()
        if conn is None:
            return []
            
        cursor = conn.cursor()
        
        sql = """
            SELECT 
                c.name_cn,
                SUM(e.amount) as total_amount
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE e.expense_date >= ? AND e.expense_date <= ?
            GROUP BY c.id, c.name_cn
            ORDER BY total_amount DESC
        """
        
        cursor.execute(sql, (start_date, end_date))
        results = cursor.fetchall()
        
        # 转换为字典列表
        statistics = []
        for row in results:
            statistics.append({
                'category_name': row[0],
                'total_amount': row[1]
            })
            
        return statistics
        
    except sqlite3.Error as e:

        return []
    except Exception as e:

        return []
    finally:
        if conn:
            conn.close()


def get_expenses_by_date(expense_date):
    """
    获取指定日期的所有支出记录，包含序号信息
    
    Args:
        expense_date (str): 日期 (YYYY-MM-DD格式)
        
    Returns:
        list: 支出记录列表，每个记录包含完整信息和序号
    """
    conn = None
    try:
        conn = create_connection()
        if conn is None:
            return []
            
        cursor = conn.cursor()
        
        # 联表查询获取完整信息
        cursor.execute("""
            SELECT e.id, e.expense_date, e.amount, e.notes, e.sequence_number,
                   c.name_cn, c.name_ug, c.id as category_id,
                   u.username
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            JOIN users u ON e.user_id = u.id
            WHERE e.expense_date = ?
            ORDER BY c.name_cn, e.sequence_number
        """, (expense_date,))
        
        rows = cursor.fetchall()
        
        result = []
        for row in rows:
            result.append({
                'id': row[0],
                'expense_date': row[1],
                'amount': row[2],
                'notes': row[3],
                'sequence_number': row[4],
                'category_name_cn': row[5],
                'category_name_ug': row[6],
                'category_id': row[7],
                'username': row[8]
            })
        
        return result
        
    except sqlite3.Error as e:

        return []
    except Exception as e:

        return []
    finally:
        if conn:
            conn.close()


def update_expense(expense_id, amount, notes):
    """
    更新支出记录的金额和备注
    
    Args:
        expense_id (int): 支出记录ID
        amount (float): 新的金额
        notes (str): 新的备注
        
    Returns:
        bool: 成功返回True，失败返回False
    """
    conn = None
    try:
        conn = create_connection()
        if conn is None:
            return False
            
        cursor = conn.cursor()
        
        # 更新记录
        cursor.execute("""
            UPDATE expenses 
            SET amount = ?, notes = ?
            WHERE id = ?
        """, (amount, notes, expense_id))
        
        conn.commit()
        return cursor.rowcount > 0
        
    except sqlite3.Error as e:

        return False
    except Exception as e:

        return False
    finally:
        if conn:
            conn.close()


def delete_expense(expense_id):
    """
    删除支出记录，并重新排序序号
    
    Args:
        expense_id (int): 支出记录ID
        
    Returns:
        bool: 成功返回True，失败返回False
    """
    conn = None
    try:
        conn = create_connection()
        if conn is None:
            return False
            
        cursor = conn.cursor()
        
        # 获取要删除记录的信息，用于重新排序
        cursor.execute("""
            SELECT expense_date, category_id, sequence_number
            FROM expenses 
            WHERE id = ?
        """, (expense_id,))
        
        record_info = cursor.fetchone()
        if not record_info:
            return False
        
        expense_date, category_id, deleted_sequence = record_info
        
        # 删除记录
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        
        # 重新排序后续记录的sequence_number
        cursor.execute("""
            UPDATE expenses 
            SET sequence_number = sequence_number - 1
            WHERE expense_date = ? AND category_id = ? AND sequence_number > ?
        """, (expense_date, category_id, deleted_sequence))
        
        conn.commit()
        return True
        
    except sqlite3.Error as e:

        return False
    except Exception as e:

        return False
    finally:
        if conn:
            conn.close()


def get_expense_summary_by_date_range(start_date, end_date):
    """
    根据指定的开始日期和结束日期，统计并返回该时间段内每个支出分类的总金额
    
    Args:
        start_date (str): 开始日期，格式为 'YYYY-MM-DD'
        end_date (str): 结束日期，格式为 'YYYY-MM-DD'
        
    Returns:
        list: 包含分类汇总信息的字典列表，每个字典包含：
              - 'category_cn': 中文分类名称
              - 'total_amount': 该分类在指定时间段内的总金额
              按总金额降序排列
              例如：[{'category_cn': '羊肉', 'total_amount': 5250.7}, 
                    {'category_cn': '蔬菜', 'total_amount': 1340.0}]
    """
    conn = None
    try:
        conn = create_connection()
        if conn is None:
            return []
            
        cursor = conn.cursor()
        
        # 联表查询，按分类统计指定日期范围内的支出总额
        sql = """
            SELECT 
                c.name_cn,
                SUM(e.amount) as total_amount
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE e.expense_date >= ? AND e.expense_date <= ?
            GROUP BY c.name_cn
            ORDER BY total_amount DESC
        """
        
        cursor.execute(sql, (start_date, end_date))
        results = cursor.fetchall()
        
        # 转换为字典列表
        summary = []
        for row in results:
            summary.append({
                'category_cn': row[0],
                'total_amount': row[1]
            })
            
        return summary
        
    except sqlite3.Error as e:

        return []
    except Exception as e:

        return []
    finally:
        if conn:
            conn.close()


def delete_all_expenses_by_date(expense_date):
    """
    ⚠️ 危险操作警告！⚠️
    删除指定日期的所有支出记录
    
    🔥 警告：这是一个极其危险的操作！
    🔥 此函数将永久删除指定日期的所有支出记录，且无法恢复！
    🔥 调用此函数前必须确保用户已经明确知晓风险并确认删除！
    🔥 建议在调用前进行数据备份！
    
    Args:
        expense_date (str): 要删除记录的日期，格式为 'YYYY-MM-DD'
        
    Returns:
        int: 成功删除的记录条数
             返回 -1 表示数据库连接失败
             返回 -2 表示发生其他错误
    
    使用示例:
        deleted_count = delete_all_expenses_by_date('2024-01-15')
        if deleted_count > 0:

        elif deleted_count == 0:

        else:

    """
    conn = None
    try:
        conn = create_connection()
        if conn is None:
    
            return -1
            
        cursor = conn.cursor()
        
        # 🔥 危险操作：删除指定日期的所有支出记录
        # 使用参数化查询防止SQL注入
        cursor.execute("""
            DELETE FROM expenses WHERE expense_date = ?
        """, (expense_date,))
        
        # 获取实际删除的记录数
        deleted_count = cursor.rowcount
        
        # 提交事务
        conn.commit()
        

        return deleted_count
        
    except sqlite3.Error as e:

        if conn:
            conn.rollback()  # 回滚事务
        return -2
    except Exception as e:

        if conn:
            conn.rollback()  # 回滚事务
        return -2
    finally:
        if conn:
            conn.close()


def update_user_credentials(user_id, old_password, new_username=None, new_password=None):
    """
    安全更新用户凭据信息（用户名和/或密码）
    
    此函数提供安全的用户信息更新机制，包含以下安全特性：
    1. 验证旧密码确保操作者身份合法
    2. 使用加密存储新密码
    3. 支持选择性更新用户名和密码
    4. 完整的事务处理确保数据一致性
    
    Args:
        user_id (int): 用户ID
        old_password (str): 当前密码（明文），用于身份验证
        new_username (str, optional): 新用户名，如果不提供则不更新用户名
        new_password (str, optional): 新密码（明文），如果不提供则不更新密码
        
    Returns:
        tuple: (success: bool, message: str)
               success为True表示更新成功，False表示失败
               message包含操作结果的详细信息
               
    使用示例:
        # 仅更新密码
        success, msg = update_user_credentials(1, "old123", new_password="new456")
        
        # 仅更新用户名
        success, msg = update_user_credentials(1, "old123", new_username="newuser")
        
        # 同时更新用户名和密码
        success, msg = update_user_credentials(1, "old123", "newuser", "new456")
    """
    conn = None
    try:
        # 参数验证
        if not user_id or not old_password:
            return False, "用户ID和旧密码不能为空"
        
        if not new_username and not new_password:
            return False, "必须提供新用户名或新密码中的至少一个"
        
        # 连接数据库
        conn = create_connection()
        if conn is None:
            return False, "数据库连接失败"
            
        cursor = conn.cursor()
        
        # 第一步：验证用户ID和旧密码
        cursor.execute("""
            SELECT username, password FROM users WHERE id = ?
        """, (user_id,))
        
        user_record = cursor.fetchone()
        if not user_record:
            return False, "用户不存在"
        
        current_username, stored_password = user_record
        
        # 验证旧密码
        old_password_hash = hash_password(old_password)
        
        # 兼容性处理：如果存储的密码不是哈希格式，先转换
        if len(stored_password) != 64:  # SHA256哈希长度为64位
            stored_password = hash_password(stored_password)
        
        if stored_password != old_password_hash:
            return False, "旧密码错误，身份验证失败"
        
        # 第二步：准备更新数据
        update_fields = []
        update_values = []
        
        # 检查是否需要更新用户名
        if new_username:
            new_username = new_username.strip()
            if not new_username:
                return False, "新用户名不能为空"
            
            # 检查新用户名是否已存在（排除当前用户）
            cursor.execute("""
                SELECT id FROM users WHERE username = ? AND id != ?
            """, (new_username, user_id))
            
            if cursor.fetchone():
                return False, f"用户名 '{new_username}' 已存在，请选择其他用户名"
            
            update_fields.append("username = ?")
            update_values.append(new_username)
        
        # 检查是否需要更新密码
        if new_password:
            new_password = new_password.strip()
            if not new_password:
                return False, "新密码不能为空"
            
            if len(new_password) < 3:
                return False, "新密码长度至少为3位"
            
            # 加密新密码
            new_password_hash = hash_password(new_password)
            update_fields.append("password = ?")
            update_values.append(new_password_hash)
        
        # 第三步：执行更新操作
        if update_fields:
            update_sql = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
            update_values.append(user_id)
            
            cursor.execute(update_sql, update_values)
            
            if cursor.rowcount == 0:
                return False, "更新失败，未影响任何记录"
            
            # 提交事务
            conn.commit()
            
            # 构建成功消息
            updated_items = []
            if new_username:
                updated_items.append(f"用户名已更新为 '{new_username}'")
            if new_password:
                updated_items.append("密码已成功更新")
            
            success_message = "用户信息更新成功：" + "，".join(updated_items)
            return True, success_message
        
        return False, "没有需要更新的内容"
        
    except sqlite3.IntegrityError as e:
        if conn:
            conn.rollback()
        return False, f"数据完整性错误：{str(e)}"
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        return False, f"数据库操作失败：{str(e)}"
    except Exception as e:
        if conn:
            conn.rollback()
        return False, f"更新用户信息时发生错误：{str(e)}"
    finally:
        if conn:
            conn.close()


def save_last_username(username):
    """
    保存最后登录的用户名到文件
    
    Args:
        username (str): 用户名
    """
    try:
        with open('last_user.txt', 'w', encoding='utf-8') as f:
            f.write(username)
    except Exception:
        pass  # 静默处理错误


def get_last_username():
    """
    从文件中读取最后登录的用户名
    
    Returns:
        str: 最后登录的用户名，如果文件不存在或读取失败则返回空字符串
    """
    try:
        with open('last_user.txt', 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception:
        return ""


def add_category(name_cn, name_ug, emoji='📝'):
    """
    添加新的支出分类
    
    Args:
        name_cn (str): 中文分类名称
        name_ug (str): 维语分类名称
        emoji (str): 表情图标，默认为📝
        
    Returns:
        tuple: (success: bool, message: str, category_id: int or None)
    """
    conn = None
    try:
        # 验证输入
        if not name_cn or not name_cn.strip():
            return False, "中文分类名称不能为空", None
        if not name_ug or not name_ug.strip():
            return False, "维语分类名称不能为空", None
        
        name_cn = name_cn.strip()
        name_ug = name_ug.strip()
        
        conn = create_connection()
        if conn is None:
            return False, "数据库连接失败", None
            
        cursor = conn.cursor()
        
        # 检查中文名称是否已存在
        cursor.execute("SELECT id FROM categories WHERE name_cn = ?", (name_cn,))
        if cursor.fetchone():
            return False, f"中文分类名称 '{name_cn}' 已存在", None
        
        # 检查维语名称是否已存在
        cursor.execute("SELECT id FROM categories WHERE name_ug = ?", (name_ug,))
        if cursor.fetchone():
            return False, f"维语分类名称 '{name_ug}' 已存在", None
        
        # 插入新分类
        cursor.execute("""
            INSERT INTO categories (name_cn, name_ug, emoji) 
            VALUES (?, ?, ?)
        """, (name_cn, name_ug, emoji))
        
        category_id = cursor.lastrowid
        conn.commit()
        
        return True, f"分类 '{name_cn} / {name_ug}' 添加成功", category_id
        
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        return False, f"数据库错误：{str(e)}", None
    except Exception as e:
        if conn:
            conn.rollback()
        return False, f"添加分类时发生错误：{str(e)}", None
    finally:
        if conn:
            conn.close()


def delete_category(category_id):
    """
    删除支出分类
    
    Args:
        category_id (int): 要删除的分类ID
        
    Returns:
        tuple: (success: bool, message: str)
    """
    conn = None
    try:
        conn = create_connection()
        if conn is None:
            return False, "数据库连接失败"
            
        cursor = conn.cursor()
        
        # 检查分类是否存在
        cursor.execute("SELECT name_cn, name_ug FROM categories WHERE id = ?", (category_id,))
        category = cursor.fetchone()
        if not category:
            return False, "分类不存在"
        
        name_cn, name_ug = category
        
        # 检查是否有支出记录使用该分类
        cursor.execute("SELECT COUNT(*) FROM expenses WHERE category_id = ?", (category_id,))
        expense_count = cursor.fetchone()[0]
        
        if expense_count > 0:
            return False, f"分类 '{name_cn} / {name_ug}' 正在被 {expense_count} 条支出记录使用，无法删除"
        
        # 删除分类
        cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        conn.commit()
        
        return True, f"分类 '{name_cn} / {name_ug}' 删除成功"
        
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        return False, f"数据库错误：{str(e)}"
    except Exception as e:
        if conn:
            conn.rollback()
        return False, f"删除分类时发生错误：{str(e)}"
    finally:
        if conn:
            conn.close()


def check_category_usage(category_id):
    """
    检查分类是否被支出记录使用
    
    Args:
        category_id (int): 分类ID
        
    Returns:
        tuple: (is_used: bool, count: int, message: str)
    """
    conn = None
    try:
        conn = create_connection()
        if conn is None:
            return False, 0, "数据库连接失败"
            
        cursor = conn.cursor()
        
        # 检查分类是否存在
        cursor.execute("SELECT name_cn, name_ug FROM categories WHERE id = ?", (category_id,))
        category = cursor.fetchone()
        if not category:
            return False, 0, "分类不存在"
        
        name_cn, name_ug = category
        
        # 检查使用情况
        cursor.execute("SELECT COUNT(*) FROM expenses WHERE category_id = ?", (category_id,))
        expense_count = cursor.fetchone()[0]
        
        if expense_count > 0:
            return True, expense_count, f"分类 '{name_cn} / {name_ug}' 被 {expense_count} 条支出记录使用"
        else:
            return False, 0, f"分类 '{name_cn} / {name_ug}' 未被使用，可以安全删除"
        
    except sqlite3.Error as e:
        return False, 0, f"数据库错误：{str(e)}"
    except Exception as e:
        return False, 0, f"检查分类使用情况时发生错误：{str(e)}"
    finally:
        if conn:
            conn.close()


def update_category(category_id, name_cn=None, name_ug=None, emoji=None):
    """
    更新分类信息
    
    Args:
        category_id (int): 分类ID
        name_cn (str, optional): 新的中文名称
        name_ug (str, optional): 新的维语名称
        emoji (str, optional): 新的表情图标
        
    Returns:
        tuple: (success: bool, message: str)
    """
    conn = None
    try:
        # 至少需要更新一个字段
        if not name_cn and not name_ug and not emoji:
            return False, "请至少指定一个要更新的字段"
        
        conn = create_connection()
        if conn is None:
            return False, "数据库连接失败"
            
        cursor = conn.cursor()
        
        # 检查分类是否存在
        cursor.execute("SELECT name_cn, name_ug FROM categories WHERE id = ?", (category_id,))
        category = cursor.fetchone()
        if not category:
            return False, "分类不存在"
        
        old_name_cn, old_name_ug = category
        
        # 构建更新语句
        update_fields = []
        params = []
        
        if name_cn and name_cn.strip():
            name_cn = name_cn.strip()
            # 检查中文名称是否与其他分类冲突
            cursor.execute("SELECT id FROM categories WHERE name_cn = ? AND id != ?", (name_cn, category_id))
            if cursor.fetchone():
                return False, f"中文分类名称 '{name_cn}' 已被其他分类使用"
            update_fields.append("name_cn = ?")
            params.append(name_cn)
        
        if name_ug and name_ug.strip():
            name_ug = name_ug.strip()
            # 检查维语名称是否与其他分类冲突
            cursor.execute("SELECT id FROM categories WHERE name_ug = ? AND id != ?", (name_ug, category_id))
            if cursor.fetchone():
                return False, f"维语分类名称 '{name_ug}' 已被其他分类使用"
            update_fields.append("name_ug = ?")
            params.append(name_ug)
        
        if emoji and emoji.strip():
            emoji = emoji.strip()
            update_fields.append("emoji = ?")
            params.append(emoji)
        
        if not update_fields:
            return False, "没有有效的更新内容"
        
        # 执行更新
        params.append(category_id)
        sql = f"UPDATE categories SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(sql, params)
        conn.commit()
        
        # 获取更新后的分类信息
        cursor.execute("SELECT name_cn, name_ug FROM categories WHERE id = ?", (category_id,))
        new_category = cursor.fetchone()
        new_name_cn, new_name_ug = new_category
        
        return True, f"分类更新成功：'{new_name_cn} / {new_name_ug}'"
        
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        return False, f"数据库错误：{str(e)}"
    except Exception as e:
        if conn:
            conn.rollback()
        return False, f"更新分类时发生错误：{str(e)}"
    finally:
        if conn:
            conn.close()


def get_all_users():
    """
    获取所有用户信息
    
    Returns:
        list: 用户信息列表，每个元素为 (user_id, username)
    """
    conn = None
    try:
        conn = create_connection()
        if conn is None:
            return []
            
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM users ORDER BY id")
        users = cursor.fetchall()
        
        return users
        
    except sqlite3.Error as e:

        return []
    except Exception as e:

        return []
    finally:
        if conn:
            conn.close()


def add_user(username, password):
    """
    添加新用户
    
    Args:
        username (str): 用户名
        password (str): 密码
        
    Returns:
        bool: 添加是否成功
    """
    conn = None
    try:
        if not username or not password:
            return False
            
        username = username.strip()
        if len(username) < 3:
            return False
            
        conn = create_connection()
        if conn is None:
            return False
            
        cursor = conn.cursor()
        
        # 检查用户名是否已存在
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            return False  # 用户名已存在
        
        
        # 添加新用户
        hashed_password = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, hashed_password, 'user')
        )
        
        conn.commit()
        return True
        
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        return False
    except Exception as e:
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def delete_user(user_id):
    """
    删除用户
    
    Args:
        user_id (int): 用户ID
        
    Returns:
        bool: 删除是否成功
    """
    conn = None
    try:
        conn = create_connection()
        if conn is None:
            return False
            
        cursor = conn.cursor()
        
        # 检查用户是否存在
        cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            return False
        
        username = user[0]
        
        # 不能删除admin用户
        if username == "admin":
            return False
        
        # 检查用户是否有支出记录
        cursor.execute("SELECT COUNT(*) FROM expenses WHERE user_id = ?", (user_id,))
        expense_count = cursor.fetchone()[0]
        
        if expense_count > 0:
            return False  # 用户有支出记录，不能删除
        
        # 删除用户
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        
        return True
        
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        return False
    except Exception as e:
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()
