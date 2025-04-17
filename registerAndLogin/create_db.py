import mysql.connector

# 数据库连接配置
config = {      
    'user': 'root',
    'password': 'dr20040722',   # 请根据本地数据库情况修改
    'host': '127.0.0.1',    # 请根据本地数据库情况修改
    'port': '3306'          # 请根据本地数据库情况修改
}

try:
    # 连接到MySQL服务器
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()

    # 删除数据库（如果存在）
    cursor.execute("DROP DATABASE IF EXISTS lingxi")
    print("数据库 'lingxi' 已删除（如果存在）")

    # 创建数据库
    cursor.execute("CREATE DATABASE lingxi CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    print("数据库 'lingxi' 创建成功！")

except mysql.connector.Error as err:
    print(f"错误: {err}")
finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL连接已关闭")

# 初始化数据插入函数
def insert_initial_data():
    try:
        # 连接到MySQL服务器并选择lingxi数据库
        config['database'] = 'lingxi'
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        # 插入管理员用户
        admin_data = {
            'username': 'admin',
            'phone_number': '13800000000',
            'email': 'admin@lingxi.com',
            'password': 'pbkdf2_sha256$600000$...',  # 实际使用时需要生成加密密码
            'is_active': True,
            'is_admin': True
        }
        
        insert_query = """
        INSERT INTO user_user
        (username, phone_number, email, password, is_active, is_admin, last_login)
        VALUES (%(username)s, %(phone_number)s, %(email)s, %(password)s, %(is_active)s, %(is_admin)s, NULL)
        """
        
        cursor.execute(insert_query, admin_data)
        connection.commit()
        print("管理员用户初始化数据插入成功！")

    except mysql.connector.Error as err:
        print(f"初始化数据插入错误: {err}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

# 执行初始化数据插入
if __name__ == "__main__":
    insert_initial_data()