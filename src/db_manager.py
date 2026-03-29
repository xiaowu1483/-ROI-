# 模块2：负责连接数据库、建表、存数据 (重点练SQL)
# TODO: Implement logic here
import sqlite3
import pandas as pd
import os

DB_NAME = 'data/processed_data.db'

def init_db():
    """
    初始化数据库，创建表结构
    """
    # 确保 data 文件夹存在
    if not os.path.exists('data'):
        os.makedirs('data')
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 创建表 (SQL DDL)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            product_id TEXT,
            category TEXT,
            ad_cost REAL,
            clicks INTEGER,
            sales_amount REAL,
            orders INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()
    print("数据库初始化完成。")

def load_data_to_db(csv_path='data/raw_data/mock_ecommerce_data.csv'):
    """
    将 CSV 数据清洗后存入数据库
    """
    if not os.path.exists(csv_path):
        print("错误：未找到数据文件，请先运行 data_generator.py")
        return

    df = pd.read_csv(csv_path)
    
    # 简单的数据清洗：去掉广告花费为空的行
    df = df.dropna(subset=['ad_cost'])
    
    conn = sqlite3.connect(DB_NAME)
    # 使用 pandas 直接写入 SQL，非常方便
    df.to_sql('daily_sales', conn, if_exists='replace', index=False)
    
    conn.close()
    print(f"成功将 {len(df)} 条数据存入数据库。")

def query_top_products(limit=5):
    """
    使用 SQL 查询销售额最高的商品 (练习 SQL 聚合查询)
    """
    conn = sqlite3.connect(DB_NAME)
    query = f"""
        SELECT product_id, SUM(sales_amount) as total_sales
        FROM daily_sales
        GROUP BY product_id
        ORDER BY total_sales DESC
        LIMIT {limit}
    """
    result = pd.read_sql_query(query, conn)
    conn.close()
    return result

if __name__ == "__main__":
    init_db()
    load_data_to_db()
    print("Top 5 商品:\n", query_top_products())
