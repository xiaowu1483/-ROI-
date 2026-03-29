# Streamlit网页入口 (你的最终展示界面)
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from src.analysis import get_full_data, calculate_metrics, find_loss_products

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="电商广告数据分析看板",
    page_icon="📊",
    layout="wide"
)

# ==================== 标题 ====================
st.title("📊 电商广告 ROI 与利润分析看板")
st.markdown("---")

# ==================== 加载数据 ====================
@st.cache_data
def load_data():
    """缓存数据，避免每次刷新都重新查询"""
    try:
        df = get_full_data()
        df = calculate_metrics(df)
        return df
    except Exception as e:
        st.error(f"数据加载失败：{e}")
        return None

df = load_data()

if df is not None:
    # ==================== 核心指标卡片 ====================
    st.subheader(" 核心指标概览")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_sales = df['sales_amount'].sum()
    total_ad_cost = df['ad_cost'].sum()
    avg_roi = df['ROI'].mean()
    total_profit = df['estimated_profit'].sum()
    
    col1.metric("总销售额", f"¥{total_sales:,.2f}")
    col2.metric("总广告花费", f"¥{total_ad_cost:,.2f}")
    col3.metric("平均 ROI", f"{avg_roi:.2f}")
    col4.metric("估算总利润", f"¥{total_profit:,.2f}", 
                delta="盈利" if total_profit > 0 else "亏损")
    
    st.markdown("---")
    
    # ==================== 侧边栏筛选 ====================
    st.sidebar.header(" 数据筛选")
    
    # 商品筛选
    all_products = df['product_id'].unique()
    selected_products = st.sidebar.multiselect(
        "选择商品",
        options=all_products,
        default=all_products[:3]  # 默认选前 3 个
    )
    
    # 时间筛选
    min_date = pd.to_datetime(df['date']).min()
    max_date = pd.to_datetime(df['date']).max()
    date_range = st.sidebar.date_input(
        "选择日期范围",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # 应用筛选
    if selected_products and len(date_range) == 2:
        df_filtered = df[
            (df['product_id'].isin(selected_products)) &
            (pd.to_datetime(df['date']) >= pd.to_datetime(date_range[0])) &
            (pd.to_datetime(df['date']) <= pd.to_datetime(date_range[1]))
        ]
    else:
        df_filtered = df
    
    # ==================== 图表区域 ====================
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📉 每日 ROI 趋势")
        roi_by_date = df_filtered.groupby('date')['ROI'].mean().reset_index()
        fig_roi = px.line(
            roi_by_date, 
            x='date', 
            y='ROI',
            title="平均 ROI 变化趋势",
            markers=True
        )
        fig_roi.add_hline(y=1.0, line_dash="dash", line_color="red", 
                         annotation_text="盈亏平衡线 (ROI=1)")
        st.plotly_chart(fig_roi, use_container_width=True)
    
    with col2:
        st.subheader("💰 商品利润对比")
        profit_by_product = df_filtered.groupby('product_id')['estimated_profit'].sum().reset_index()
        profit_by_product = profit_by_product.sort_values('estimated_profit', ascending=True)
        fig_profit = px.bar(
            profit_by_product,
            x='estimated_profit',
            y='product_id',
            orientation='h',
            title="各商品总利润",
            color='estimated_profit',
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig_profit, use_container_width=True)
    
    # ==================== 第二行图表 ====================
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("🎯 广告花费 vs 销售额")
        scatter_df = df_filtered.groupby('product_id').agg({
            'ad_cost': 'sum',
            'sales_amount': 'sum'
        }).reset_index()
        fig_scatter = px.scatter(
            scatter_df,
            x='ad_cost',
            y='sales_amount',
            size='sales_amount',
            color='product_id',
            hover_name='product_id',
            title="广告投入产出散点图",
            labels={'ad_cost': '广告花费', 'sales_amount': '销售额'}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with col4:
        st.subheader(" 转化率分析")
        cvr_by_product = df_filtered.groupby('product_id').agg({
            'orders': 'sum',
            'clicks': 'sum'
        }).reset_index()
        cvr_by_product['CVR'] = cvr_by_product['orders'] / cvr_by_product['clicks'].replace(0, 1)
        fig_cvr = px.bar(
            cvr_by_product,
            x='product_id',
            y='CVR',
            title="各商品转化率 (CVR)",
            color='CVR',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_cvr, use_container_width=True)
    
    # ==================== 亏损商品预警 ====================
    st.markdown("---")
    st.subheader("⚠️ 亏损商品预警")
    
    loss_products = find_loss_products(df_filtered)
    
    if len(loss_products) > 0:
        st.error(f"发现 {len(loss_products)} 个平均利润为负的商品！")
        st.dataframe(
            loss_products.style.format({'estimated_profit': '¥{:.2f}'}),
            use_container_width=True
        )
        st.info("💡 建议：考虑降低这些商品的广告出价，或优化商品详情页提升转化。")
    else:
        st.success("✅ 所有商品目前均为盈利状态！")
    
    # ==================== 原始数据展示 ====================
    with st.expander("📋 查看原始数据"):
        st.dataframe(df_filtered, use_container_width=True)
        
        # 提供下载按钮
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=" 下载筛选后的数据 (CSV)",
            data=csv,
            file_name='filtered_ecommerce_data.csv',
            mime='text/csv'
        )

else:
    st.warning("⚠️ 未找到数据，请先运行数据生成脚本")
    st.code("""
    # 在终端运行以下命令生成数据：
    python src/data_generator.py
    python src/db_manager.py
    """)

# ==================== 页脚 ====================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <small>电商广告数据分析系统 | Powered by Python & Streamlit</small>
    </div>
    """,
    unsafe_allow_html=True
)
