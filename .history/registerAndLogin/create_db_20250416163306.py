import mysql.connector

# 数据库连接配置
config = {      
    'user': 'root',
    'password': '030607',   # 请根据本地数据库情况修改
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