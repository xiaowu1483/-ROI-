import pandas as pd
import sqlite3

DB_NAME = 'data/processed_data.db'

def get_full_data():
    """从数据库读取所有数据"""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM daily_sales", conn)
    conn.close()
    return df

def calculate_metrics(df):
    """
    计算核心电商指标
    """
    # 1. 数据预处理：防止除以零错误
    # 将 clicks 为 0 的地方替换为 1，避免计算转化率时报错
    df['safe_clicks'] = df['clicks'].replace(0, 1)
    df['safe_ad_cost'] = df['ad_cost'].replace(0, 1)
    
    # 2. 计算 ROI (投入产出比) = 销售额 / 广告费
    df['ROI'] = df['sales_amount'] / df['safe_ad_cost']
    
    # 3. 计算 CPC (单次点击成本) = 广告费 / 点击量
    df['CPC'] = df['ad_cost'] / df['safe_clicks']
    
    # 4. 计算 CVR (转化率) = 订单量 / 点击量
    df['CVR'] = df['orders'] / df['safe_clicks']
    
    # 5. 估算利润 (假设毛利率为 30%)
    # 利润 = 销售额 * 0.3 - 广告费
    df['estimated_profit'] = (df['sales_amount'] * 0.3) - df['ad_cost']
    
    return df

def find_loss_products(df):
    """
    业务分析：找出“亏损”的商品 (利润 < 0)
    这是 JD 中提到的“协助维护店铺健康度”
    """
    # 按商品分组，计算平均利润
    product_profit = df.groupby('product_id')['estimated_profit'].mean().reset_index()
    
    # 筛选出平均利润小于 0 的商品
    loss_products = product_profit[product_profit['estimated_profit'] < 0]
    
    return loss_products

if __name__ == "__main__":
    df = get_full_data()
    df_metrics = calculate_metrics(df)
    
    print("数据前 5 行预览：")
    print(df_metrics[['product_id', 'ROI', 'estimated_profit']].head())
    
    print("\n--- 亏损商品预警 ---")
    loss_df = find_loss_products(df_metrics)
    if len(loss_df) > 0:
        print("发现以下商品平均利润为负，建议调整广告策略：")
        print(loss_df)
    else:
        print("所有商品目前均为盈利状态。")
