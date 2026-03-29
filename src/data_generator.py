# 模块1：负责“造”模拟数据
# TODO: Implement logic here
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_ecommerce_data(rows=500):
    """
    生成模拟的电商广告与销售数据
    """
    print("正在生成模拟数据...")
    
    # 1. 基础信息
    products = ['A001-连衣裙', 'A002-运动鞋', 'A003-蓝牙耳机', 'A004-保温杯', 'A005-手机壳']
    categories = ['服装', '鞋履', '数码', '家居', '配件']
    
    # 2. 生成日期 (过去30天)
    end_date = datetime.now()
    dates = [end_date - timedelta(days=x) for x in range(rows)]
    dates.sort() # 让时间有序
    
    data = {
        'date': dates,
        'product_id': [random.choice(products) for _ in range(rows)],
        'category': [random.choice(categories) for _ in range(rows)],
        'ad_cost': np.random.uniform(50, 2000, rows), # 广告花费 50-2000元
        'clicks': np.random.randint(10, 5000, rows),  # 点击量
        'sales_amount': np.random.uniform(100, 10000, rows), # 销售额
        'orders': np.random.randint(1, 100, rows)     # 订单量
    }
    
    df = pd.DataFrame(data)
    
    # 3. 制造一点“脏数据” (模拟真实情况)
    # 故意让几行的广告花费为 NaN，测试后续的数据清洗能力
    df.loc[5, 'ad_cost'] = np.nan 
    # 故意让几行的点击量为 0 (会导致除以零错误，测试异常处理)
    df.loc[10, 'clicks'] = 0 
    
    # 4. 保存为 CSV (供后续使用)
    # 注意：实际项目中，raw_data 通常不上传到 GitHub
    df.to_csv('data/raw_data/mock_ecommerce_data.csv', index=False)
    print("数据已生成并保存至 data/raw_data/mock_ecommerce_data.csv")
    
    return df

if __name__ == "__main__":
    generate_ecommerce_data()
