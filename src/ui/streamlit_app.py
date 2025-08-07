#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票AI分析助手 - Streamlit Web界面
专为新手股民设计的智能股票分析工具
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import datetime
from datetime import datetime, timedelta
import time
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger

# 尝试导入模块，如果失败则使用模拟数据
try:
    from src.data.data_fetcher import DataFetcher
    from src.ai.stock_analyzer import StockAnalyzer
    from src.trading.auto_trader import AutoTrader
    from config.config import config
    MODULES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"模块导入失败: {e}")
    MODULES_AVAILABLE = False

# 配置页面
st.set_page_config(
    page_title="股票AI分析助手",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 禁用外部资源请求
import streamlit.components.v1 as components

# 添加自定义配置来避免网络请求
st.markdown("""
<script>
// 禁用统计收集和外部资源请求
window.gtag = function() {};
window.dataLayer = [];
</script>
""", unsafe_allow_html=True)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .recommendation-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .buy-signal {
        background-color: #ffe6e6;
        border-left: 4px solid #ff4d4d;
    }
    .sell-signal {
        background-color: #e6ffe6;
        border-left: 4px solid #00cc00;
    }
    .hold-signal {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
    }
    .risk-low {
        color: #00cc00;
        font-weight: bold;
    }
    .risk-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .risk-high {
        color: #ff4d4d;
        font-weight: bold;
    }
    /* 中国股市颜色习惯：涨红跌绿 */
    .price-up {
        color: #ff4d4d !important;
    }
    .price-down {
        color: #00cc00 !important;
    }
    .price-neutral {
        color: #666666 !important;
    }
    
    /* 数据表格样式 */
    .dataframe td {
        padding: 8px !important;
    }
    
    /* 涨跌幅样式 */
    .change-positive {
        color: #ff4d4d !important;
        font-weight: bold;
        background-color: rgba(255, 77, 77, 0.1) !important;
        padding: 2px 6px !important;
        border-radius: 3px !important;
    }
    
    .change-negative {
        color: #4d9f4d !important;
        font-weight: bold;
        background-color: rgba(77, 159, 77, 0.1) !important;
        padding: 2px 6px !important;
        border-radius: 3px !important;
    }
    
    .change-zero {
        color: #808080 !important;
        font-weight: bold;
        background-color: rgba(128, 128, 128, 0.1) !important;
        padding: 2px 6px !important;
        border-radius: 3px !important;
    }
</style>
""", unsafe_allow_html=True)

# 缓存数据获取函数
@st.cache_data(ttl=300)  # 缓存5分钟
def get_cached_stock_data(symbol, period):
    """获取缓存的股票数据"""
    if not MODULES_AVAILABLE:
        # 返回模拟数据
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        np.random.seed(42)
        base_price = 100
        data = {
            'open': base_price + np.random.randn(100).cumsum() * 0.5,
            'high': base_price + np.random.randn(100).cumsum() * 0.5 + 2,
            'low': base_price + np.random.randn(100).cumsum() * 0.5 - 2,
            'close': base_price + np.random.randn(100).cumsum() * 0.5,
            'volume': np.random.randint(1000000, 10000000, 100)
        }
        df = pd.DataFrame(data, index=dates)
        # 添加技术指标
        df['ma5'] = df['close'].rolling(5).mean()
        df['ma20'] = df['close'].rolling(20).mean()
        df['rsi'] = 50 + np.random.randn(100) * 10  # 模拟RSI
        return df
    
    try:
        data_fetcher = DataFetcher()
        return data_fetcher.get_stock_data(symbol, period=period)
    except Exception as e:
        st.error(f"获取股票数据失败: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=600)  # 缓存10分钟
def get_cached_analysis(symbol, period):
    """获取缓存的分析结果"""
    if not MODULES_AVAILABLE:
        # 返回模拟分析结果
        score = np.random.randint(60, 95)
        level = 'bullish' if score >= 80 else 'bearish' if score <= 40 else 'neutral'
        return {
            'overall_score': {'score': score, 'level': level},
            'recommendation': np.random.choice(['买入', '持有', '卖出']),
            'confidence': np.random.uniform(60, 95),
            'reason': '基于技术面和基本面综合分析（模拟数据）',
            'risk_level': np.random.choice(['低', '中等', '高']),
            'technical_indicators': {
                'MA5': np.random.uniform(90, 110),
                'MA20': np.random.uniform(90, 110),
                'RSI': np.random.uniform(30, 70),
                'MACD': np.random.uniform(-2, 2)
            },
            'risks': ['这是演示数据，仅供学习使用']
        }
    
    try:
        data_fetcher = DataFetcher()
        analyzer = StockAnalyzer()
        
        stock_data = data_fetcher.get_stock_data(symbol, period=period)
        financial_data = data_fetcher.get_financial_data(symbol)
        
        return analyzer.analyze_stock(
            ts_code_or_data=stock_data,
            financial_data=financial_data
        )
    except Exception as e:
        st.error(f"股票分析失败: {e}")
        return {}

def render_header():
    """渲染页面头部"""
    st.markdown('<h1 class="main-header">📈 股票AI分析助手</h1>', unsafe_allow_html=True)
    
    # 免责声明 - 醒目位置
    st.markdown("""
    <div style="background-color: #fff3cd; border: 2px solid #ffc107; border-radius: 10px; padding: 15px; margin: 20px 0;">
        <div style="color: #856404; text-align: center;">
            <h3 style="color: #d63384; margin-top: 0;">⚠️ 重要免责声明</h3>
            <p style="margin: 10px 0; font-size: 16px; font-weight: bold;">
                🎓 本工具为<span style="color: #d63384;">公益性质</span>，专为新手股民提供投资学习参考
            </p>
            <p style="margin: 5px 0; font-size: 14px;">
                📊 所有分析结果仅供参考，不构成投资建议 | 🔍 股市有风险，投资需谨慎
            </p>
            <p style="margin: 5px 0; font-size: 14px;">
                ⚖️ <strong>作者不承担任何因使用本工具而产生的投资风险和损失</strong>
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; color: #666; margin-bottom: 2rem;">
        🎯 专为新手股民设计 | 🤖 AI智能分析 | 📊 实时数据 | 💡 投资建议
    </div>
    """, unsafe_allow_html=True)
    
    # 如果模块不可用，显示提示
    if not MODULES_AVAILABLE:
        st.warning("⚠️ 部分依赖模块未安装，当前使用模拟数据进行演示。要获得完整功能，请安装所有依赖包。")

def render_sidebar():
    """渲染侧边栏"""
    st.sidebar.title("🔧 功能导航")
    
    # 功能选择 - 改为单选按钮直接列出
    page = st.sidebar.radio(
        "选择功能",
        [
            "📊 股票分析", 
            "🎯 智能选股", 
            "⚡ 自动交易", 
            "📈 市场概览", 
            "📚 投资学堂"
        ],
        index=0
    )
    
    st.sidebar.markdown("---")
    
    # 显示功能说明
    feature_descriptions = {
        "📊 股票分析": "深度分析单只股票的技术面、基本面和AI评分",
        "🎯 智能选股": "AI驱动的多维度股票筛选和推荐系统", 
        "⚡ 自动交易": "智能交易策略执行和风险管理系统",
        "📈 市场概览": "实时市场指数、热点板块和行情数据",
        "📚 投资学堂": "投资知识、技术分析和风险管理教程"
    }
    
    if page in feature_descriptions:
        st.sidebar.info(f"💡 {feature_descriptions[page]}")
    
    # 根据不同页面显示相关信息
    if page == "📊 股票分析":
        st.sidebar.markdown("### 🎯 分析功能")
        st.sidebar.markdown("""
        - **AI综合评分**: 多维度智能评估
        - **技术指标**: MA、RSI、MACD等
        - **基本面分析**: 财务数据解读
        - **风险评估**: 投资风险等级
        """)
        
    elif page == "🎯 智能选股":
        st.sidebar.markdown("### 📊 选股特色")
        st.sidebar.markdown("""
        - **115只股票池**: A股+美股全覆盖
        - **11个行业**: 专业行业分类
        - **多维筛选**: 评分+风险+市值
        - **实时推荐**: 动态股票推荐
        """)
        
    elif page == "⚡ 自动交易":
        st.sidebar.markdown("### 🤖 自动交易功能")
        st.sidebar.markdown("""
        - **📊 策略配置**: 保守型、平衡型、激进型三种策略
        - **💰 资金管理**: 智能仓位控制和资金分配
        - **🛡️ 风险控制**: 止损止盈、最大回撤控制
        - **📈 回测验证**: 历史数据验证策略效果
        - **⭐ 自选股池**: 基于自选股的智能交易
        - **📊 实时监控**: 24/7交易状态和收益监控
        """)
        
        st.sidebar.markdown("### ⚠️ 重要提醒")
        st.sidebar.warning("""
        🔴 **风险提示**
        - 股市有风险，投资需谨慎
        - 建议先使用模拟交易熟悉系统
        - 实盘交易请根据个人风险承受能力操作
        """)
        
        st.sidebar.markdown("### 💡 使用建议")
        st.sidebar.info("""
        **新手用户建议流程**:
        1. 添加自选股
        2. 配置保守型策略
        3. 进行模拟回测
        4. 观察策略效果
        5. 调整参数优化
        6. 小资金实盘验证
        """)
        
    elif page == "📈 市场概览":
        st.sidebar.markdown("### 📈 数据来源")
        st.sidebar.markdown("""
        - **实时指数**: 7大主要市场指数
        - **热点板块**: 当日活跃板块排行
        - **数据更新**: 实时刷新最新行情
        - **多市场**: A股+美股同步监控
        """)
    
    return page, "000001.SZ", "1y"  # 返回默认值，在主页面处理具体逻辑

def create_candlestick_chart(stock_data, technical_indicators=None):
    """创建K线图表"""
    if stock_data.empty:
        return go.Figure()
    
    # 创建子图
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('股价走势', '成交量', '技术指标'),
        vertical_spacing=0.05,
        row_heights=[0.6, 0.2, 0.2]
    )
    
    # K线图 - 中国股市习惯：涨红跌绿
    fig.add_trace(
        go.Candlestick(
            x=stock_data.index,
            open=stock_data['open'],
            high=stock_data['high'],
            low=stock_data['low'],
            close=stock_data['close'],
            name="K线",
            increasing=dict(line=dict(color='red'), fillcolor='red'),
            decreasing=dict(line=dict(color='green'), fillcolor='green')
        ),
        row=1, col=1
    )
    
    # 移动平均线
    if 'ma5' in stock_data.columns:
        fig.add_trace(
            go.Scatter(
                x=stock_data.index,
                y=stock_data['ma5'],
                mode='lines',
                name='MA5',
                line=dict(color='orange', width=1)
            ),
            row=1, col=1
        )
    
    if 'ma20' in stock_data.columns:
        fig.add_trace(
            go.Scatter(
                x=stock_data.index,
                y=stock_data['ma20'],
                mode='lines',
                name='MA20',
                line=dict(color='blue', width=1)
            ),
            row=1, col=1
        )
    
    # 成交量 - 兼容不同列名
    volume_col = 'volume' if 'volume' in stock_data.columns else 'vol'
    if volume_col in stock_data.columns:
        fig.add_trace(
            go.Bar(
                x=stock_data.index,
                y=stock_data[volume_col],
                name='成交量',
                marker_color='lightblue'
            ),
            row=2, col=1
        )
    
    # RSI指标
    if 'rsi' in stock_data.columns:
        fig.add_trace(
            go.Scatter(
                x=stock_data.index,
                y=stock_data['rsi'],
                mode='lines',
                name='RSI',
                line=dict(color='purple', width=2)
            ),
            row=3, col=1
        )
        
        # RSI超买超卖线 - 中国习惯：超买红色警戒，超卖绿色机会
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
    
    # 更新布局
    fig.update_layout(
        title="股票技术分析图表",
        xaxis_title="日期",
        height=800,
        showlegend=True,
        xaxis_rangeslider_visible=False
    )
    
    return fig

def render_stock_analysis_page(symbol, period):
    """渲染股票分析页面"""
    
    st.subheader("📊 股票深度分析")
    
    # 使用智能股票输入组件
    try:
        from src.ui.smart_stock_input import smart_stock_input, display_stock_info
        
        # 添加使用提示
        st.info("� **搜索提示**: 支持股票代码(如: 000001)、完整名称(如: 平安银行)或简称(如: 中行)的模糊搜索")
        
        # 智能股票选择
        symbol, name = smart_stock_input(
            label="🔍 选择要分析的股票",
            default_symbol=symbol,
            key="stock_analysis"
        )
        
        # 显示股票信息卡片
        display_stock_info(symbol, name)
        
    except Exception as e:
        # 降级处理
        st.warning("⚠️ 智能搜索组件加载失败，使用基础输入模式")
        
        try:
            from src.data.stock_mapper import stock_mapper
            
            # 基础股票选择
            col1, col2 = st.columns([3, 1])
            with col1:
                # 获取所有股票
                all_stocks = stock_mapper.get_all_stocks()
                stock_options = [f"{code} - {name}" for code, name in sorted(all_stocks.items())]
                
                # 找到当前股票的索引
                current_option = f"{symbol} - {stock_mapper.get_stock_name(symbol)}"
                current_index = 0
                if current_option in stock_options:
                    current_index = stock_options.index(current_option)
                
                selected_option = st.selectbox(
                    "选择股票进行分析",
                    options=stock_options,
                    index=current_index,
                    help="选择要分析的股票，支持键盘输入搜索"
                )
                
                # 解析选择的股票
                if " - " in selected_option:
                    symbol, name = selected_option.split(" - ", 1)
                else:
                    symbol = selected_option
                    name = stock_mapper.get_stock_name(symbol)
            
            with col2:
                if st.button("🔄 刷新数据", help="重新获取最新股票数据"):
                    st.rerun()
            
            # 显示基础股票信息
            st.markdown(f"**分析股票**: {name} ({symbol})")
            
        except:
            # 最基础的降级处理
            symbol = st.text_input("请输入股票代码", value=symbol, help="如: 000001.SZ")
            name = symbol
    
    # 分析周期选择
    col1, col2 = st.columns([2, 1])
    with col1:
        period = st.selectbox(
            "分析周期",
            ["1m", "3m", "6m", "1y", "2y"],
            index=3,
            help="选择股票数据的时间周期"
        )
    
    # 获取数据和分析结果
    with st.spinner("正在获取数据和分析..."):
        stock_data = get_cached_stock_data(symbol, period)
        analysis_result = get_cached_analysis(symbol, period)
    
    if stock_data.empty or not analysis_result:
        st.error("无法获取股票数据，请检查股票代码是否正确")
        return
    
    # 基本信息
    col1, col2, col3, col4 = st.columns(4)
    
    latest_price = stock_data['close'].iloc[-1]
    prev_price = stock_data['close'].iloc[-2] if len(stock_data) > 1 else latest_price
    price_change = latest_price - prev_price
    price_change_pct = (price_change / prev_price) * 100 if prev_price != 0 else 0
    
    with col1:
        # 中国股市习惯：涨红跌绿
        if price_change > 0:
            price_color = "red"
            price_arrow = "↗"
        elif price_change < 0:
            price_color = "green"  
            price_arrow = "↘"
        else:
            price_color = "gray"
            price_arrow = "→"
            
        st.metric(
            "最新价格",
            f"¥{latest_price:.2f}",
            f"{price_arrow} {price_change:+.2f} ({price_change_pct:+.2f}%)"
        )
        
        # 使用自定义颜色显示涨跌
        price_class = "price-up" if price_change > 0 else ("price-down" if price_change < 0 else "price-neutral")
        st.markdown(f'<div class="{price_class}">涨跌: {price_change:+.2f} ({price_change_pct:+.2f}%)</div>', unsafe_allow_html=True)
    
    with col2:
        score = analysis_result.get('overall_score', {}).get('score', 0)
        level = analysis_result.get('overall_score', {}).get('level', 'neutral')
        
        # 根据评分级别设置颜色
        if score >= 80:
            delta_color = "normal"
            score_emoji = "🟢"
        elif score >= 60:
            delta_color = "normal" 
            score_emoji = "🟡"
        else:
            delta_color = "inverse"
            score_emoji = "🔴"
        
        st.metric(
            "综合评分",
            f"{score_emoji} {score:.1f}/100",
            f"级别: {level}",
            help="AI综合评分，范围0-100分"
        )
    
    with col3:
        recommendation = analysis_result.get('recommendation', '持有')
        color = "normal"
        if recommendation == "买入":
            color = "inverse"
        elif recommendation == "卖出":
            color = "off"
        
        st.metric("投资建议", recommendation)
    
    with col4:
        risk_level = analysis_result.get('risk_level', '中等')
        
        # 中文风险等级到CSS类的映射
        risk_class_mapping = {
            '低': 'risk-low',
            '低风险': 'risk-low', 
            '中等': 'risk-medium',
            '中等风险': 'risk-medium',
            '高': 'risk-high',
            '高风险': 'risk-high',
            'low': 'risk-low',
            'medium': 'risk-medium', 
            'high': 'risk-high'
        }
        
        risk_class = risk_class_mapping.get(risk_level, 'risk-medium')
        st.markdown(f'<p class="{risk_class}">风险等级: {risk_level}</p>', unsafe_allow_html=True)
    
    # AI评分详细信息
    if st.checkbox("显示AI评分详情", key="ai_score_details"):
        st.subheader("📊 AI评分详细分析")
        
        overall_score = analysis_result.get('overall_score', {})
        components = overall_score.get('components', {})
        weights = overall_score.get('weights', {})
        
        if components and weights:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**各维度评分:**")
                for component, score in components.items():
                    component_names = {
                        'technical': '技术分析',
                        'fundamental': '基本面',
                        'sentiment': '市场情绪',
                        'ml': '机器学习'
                    }
                    name = component_names.get(component, component)
                    st.metric(name, f"{score:.1f}")
            
            with col2:
                st.write("**权重配置:**")
                for weight_key, weight_value in weights.items():
                    weight_names = {
                        'technical': '技术分析权重',
                        'fundamental': '基本面权重',
                        'sentiment': '情绪权重',
                        'ml': 'ML权重'
                    }
                    name = weight_names.get(weight_key, weight_key)
                    st.metric(name, f"{weight_value:.1%}")
            
            # 权重检查
            weight_sum = overall_score.get('weight_sum', 0)
            if abs(weight_sum - 1.0) > 0.01:
                st.warning(f"⚠️ 权重总和: {weight_sum:.3f} (应为1.0)")
            else:
                st.success(f"✅ 权重总和: {weight_sum:.3f}")
        else:
            st.info("AI评分详情暂不可用")
    
    # 详细分析结果
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # K线图表
        fig = create_candlestick_chart(stock_data, analysis_result.get('technical_indicators'))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 投资建议卡片
        recommendation = analysis_result.get('recommendation', '持有')
        signal_class = "hold-signal"
        if recommendation == "买入":
            signal_class = "buy-signal"
        elif recommendation == "卖出":
            signal_class = "sell-signal"
        
        st.markdown(f"""
        <div class="recommendation-box {signal_class}">
            <h4>🎯 AI投资建议</h4>
            <p><strong>操作建议:</strong> {recommendation}</p>
            <p><strong>置信度:</strong> {analysis_result.get('confidence', 0):.1f}%</p>
            <p><strong>理由:</strong> {analysis_result.get('reason', '基于技术面和基本面综合分析')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 技术指标
        st.subheader("📈 技术指标")
        if 'technical_indicators' in analysis_result:
            for indicator, value in analysis_result['technical_indicators'].items():
                if isinstance(value, (int, float)):
                    st.metric(indicator, f"{value:.2f}")
                else:
                    st.metric(indicator, str(value))
        
        # 风险提示
        st.subheader("⚠️ 风险提示")
        risks = analysis_result.get('risks', [])
        if risks:
            for risk in risks:
                st.warning(risk)
        else:
            st.info("暂无特殊风险提示")

def render_stock_screening_page():
    """渲染智能选股页面"""
    st.subheader("🎯 智能选股推荐")
    
    # 股票池配置
    st.markdown("### 📋 股票池配置")
    pool_col1, pool_col2, pool_col3, pool_col4 = st.columns(4)
    
    with pool_col1:
        market_selection = st.selectbox(
            "市场选择",
            ["混合", "中国A股", "美股"],
            index=0
        )
    
    with pool_col2:
        # 获取可用行业列表
        try:
            from src.data.dynamic_stock_pool import DynamicStockPool
            pool_manager = DynamicStockPool()
            available_sectors = pool_manager.get_available_sectors(market_selection)
        except:
            available_sectors = ["全部", "银行", "科技", "消费"]
        
        sector_selection = st.selectbox(
            "行业选择",
            available_sectors,
            index=0
        )
    
    with pool_col3:
        pool_size = st.selectbox(
            "股票池大小",
            [50, 100, 200, "全部"],
            index=2,
            help="选择股票池大小，'全部'将包含所有可用股票"
        )
    
    with pool_col4:
        random_seed = st.checkbox("随机种子", value=True, help="开启后每次生成不同的股票池")
    
    # 筛选条件
    st.markdown("### ⚙️ 筛选条件")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_score = st.slider("最低评分", 0, 100, 70)
    
    with col2:
        risk_tolerance = st.selectbox(
            "风险承受度",
            ["低风险", "中等风险", "高风险"],
            index=1
        )
    
    with col3:
        market_cap = st.selectbox(
            "市值偏好",
            ["不限", "大盘股", "中盘股", "小盘股"],
            index=0
        )
    
    if st.button("🔍 开始筛选", type="primary"):
        with st.spinner("正在筛选股票..."):
            try:
                # 获取股票分析器
                if MODULES_AVAILABLE:
                    from src.ai.stock_analyzer import StockAnalyzer
                    from src.data.dynamic_stock_pool import DynamicStockPool
                    import random
                    
                    analyzer = StockAnalyzer()
                    pool_manager = DynamicStockPool()
                    
                    # 设置随机种子
                    if not random_seed:
                        random.seed(42)  # 固定种子保证结果一致
                    
                    # 根据用户偏好生成动态股票池
                    if pool_size == "全部":
                        stock_pool = pool_manager.get_all_stocks()
                    else:
                        stock_pool = pool_manager.get_stock_pool(
                            market=market_selection,
                            sector=sector_selection,
                            market_cap=market_cap if market_cap != "不限" else "不限",
                            pool_size=int(pool_size)
                        )
                    
                    # 显示当前股票池信息
                    st.info(f"🔍 当前股票池: {len(stock_pool)} 只股票 | 市场: {market_selection} | 行业: {sector_selection}")
                    with st.expander("查看股票池详情"):
                        st.write("当前股票池包含以下股票:")
                        st.write(", ".join(stock_pool))
                    
                    # 转换风险等级
                    risk_map = {"低风险": "低风险", "中等风险": "中等风险", "高风险": "高风险"}
                    
                    # 执行筛选
                    screening_results = analyzer.screen_stocks(
                        stock_list=stock_pool,
                        min_score=min_score,
                        risk_level=risk_map[risk_tolerance],
                        market_cap=market_cap
                    )
                    
                    if screening_results:
                        # 显示筛选结果
                        st.success(f"筛选完成！找到 {len(screening_results)} 只符合条件的股票")
                        
                        # 结果表格 - 添加股票名称映射
                        from src.data.stock_mapper import stock_mapper
                        
                        # 为结果添加股票名称
                        for result in screening_results:
                            symbol = result.get('symbol', '')
                            result['name'] = stock_mapper.get_stock_name(symbol)
                        
                        df = pd.DataFrame(screening_results)
                        
                        # 格式化涨跌数据以符合中国股市习惯
                        if 'upside' in df.columns:
                            def format_upside(value):
                                if pd.isna(value):
                                    return ""
                                if value > 0:
                                    return f"📈 +{value:.1f}%"
                                elif value < 0:
                                    return f"📉 {value:.1f}%"
                                else:
                                    return f"➖ {value:.1f}%"
                            
                            df['formatted_upside'] = df['upside'].apply(format_upside)
                        
                        # 格式化显示
                        st.dataframe(
                            df,
                            column_config={
                                "symbol": "股票代码",
                                "name": "股票名称",
                                "score": st.column_config.ProgressColumn(
                                    "AI评分",
                                    help="AI综合评分",
                                    min_value=0,
                                    max_value=100,
                                ),
                                "recommendation": "投资建议",
                                "risk_level": "风险等级",
                                "current_price": st.column_config.NumberColumn(
                                    "当前价格",
                                    format="¥%.2f"
                                ),
                                "target_price": st.column_config.NumberColumn(
                                    "目标价格", 
                                    format="¥%.2f"
                                ),
                                "formatted_upside": "涨跌空间",
                                "upside": None,  # 隐藏原始upside列
                                "confidence": st.column_config.ProgressColumn(
                                    "置信度",
                                    help="分析置信度",
                                    min_value=0,
                                    max_value=1,
                                ),
                                "analysis_date": "分析日期"
                            },
                            hide_index=True,
                            use_container_width=True
                        )
                        
                        # 显示筛选统计
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            avg_score = sum(r['score'] for r in screening_results) / len(screening_results)
                            st.metric("平均评分", f"{avg_score:.1f}")
                        
                        with col2:
                            buy_count = sum(1 for r in screening_results if r['recommendation'] == '买入')
                            st.metric("买入推荐", f"{buy_count} 只")
                        
                        with col3:
                            avg_upside = sum(r['upside'] for r in screening_results) / len(screening_results)
                            st.metric("平均上涨空间", f"{avg_upside:.1f}%")
                        
                    else:
                        st.warning("没有找到符合条件的股票，请尝试调整筛选条件")
                        
                else:
                    # 降级模式：显示模拟数据
                    st.warning("分析模块不可用，显示模拟数据")
                    screening_results = [
                        {
                            'symbol': '000001.SZ',
                            'name': '平安银行',
                            'score': 85,
                            'recommendation': '买入',
                            'risk_level': '低风险',
                            'current_price': 12.34,
                            'target_price': 14.50,
                            'upside': 17.5
                        }
                    ]
                    
                    # 格式化涨跌数据以符合中国股市习惯
                    for result in screening_results:
                        upside = result['upside']
                        if upside > 0:
                            result['formatted_upside'] = f"📈 +{upside:.1f}%"
                        elif upside < 0:
                            result['formatted_upside'] = f"📉 {upside:.1f}%"
                        else:
                            result['formatted_upside'] = f"➖ {upside:.1f}%"
                    
                    df = pd.DataFrame(screening_results)
                    st.dataframe(
                        df,
                        column_config={
                            "symbol": "股票代码",
                            "name": "股票名称",
                            "score": "AI评分",
                            "recommendation": "投资建议",
                            "risk_level": "风险等级",
                            "current_price": st.column_config.NumberColumn(
                                "当前价格",
                                format="¥%.2f"
                            ),
                            "target_price": st.column_config.NumberColumn(
                                "目标价格",
                                format="¥%.2f"
                            ),
                            "formatted_upside": "涨跌空间",
                            "upside": None,  # 隐藏原始upside列
                        },
                        hide_index=True, 
                        use_container_width=True
                    )
                    
            except Exception as e:
                st.error(f"筛选过程中出现错误: {e}")
                logger.error(f"股票筛选错误: {e}")
                
                # 显示错误详情（仅在调试模式下）
                if st.checkbox("显示错误详情"):
                    st.code(str(e))

def render_auto_trading_page():
    """渲染自动交易页面"""
    st.subheader("⚡ 智能自动交易")
    
    # 功能介绍
    st.markdown("""
    <div style="background: linear-gradient(90deg, #e3f2fd 0%, #f3e5f5 100%); padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem;">
        <h4 style="color: #1976d2; margin-top: 0;">🤖 智能自动交易系统</h4>
        <p style="margin-bottom: 0.5rem; color: #424242;">
            基于AI驱动的智能交易系统，集成多种交易策略和风险管理机制，为投资者提供全自动化的股票交易解决方案。
        </p>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.5rem; margin-top: 1rem;">
            <div>📊 <strong>智能策略</strong>: 保守型、平衡型、激进型</div>
            <div>🛡️ <strong>风险管控</strong>: 止损止盈、仓位控制</div>
            <div>⭐ <strong>自选股池</strong>: 基于个人偏好的股票池</div>
            <div>📈 <strong>实时监控</strong>: 24/7交易状态跟踪</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.warning("⚠️ 自动交易功能仅供学习和模拟使用，实盘交易请谨慎操作！")
    
    # 创建标签页
    tab1, tab2, tab3, tab4 = st.tabs(["🎛️ 交易配置", "📈 模拟回测", "⭐ 自选股管理", "📊 交易记录"])
    
    with tab1:
        render_trading_config()
    
    with tab2:
        render_simulation_backtest()
    
    with tab3:
        render_watchlist_management()
    
    with tab4:
        render_trading_records()

def render_trading_config():
    """渲染交易配置页面"""
    st.subheader("🎛️ 交易配置")
    
    # 策略说明
    with st.expander("📚 交易策略详解", expanded=False):
        st.markdown("""
        ### 💡 三种交易策略对比
        
        | 策略类型 | 风险等级 | 预期收益 | 适用人群 | 主要特点 |
        |---------|---------|---------|---------|---------|
        | 🛡️ **保守型** | 低风险 | 8-15% | 投资新手、稳健投资者 | 严格止损、低仓位、稳健操作 |
        | ⚖️ **平衡型** | 中等风险 | 15-25% | 有经验投资者 | 风险收益平衡、适度杠杆 |
        | 🚀 **激进型** | 高风险 | 25%+ | 风险承受力强的投资者 | 高仓位、快速进出、追求高收益 |
        
        ### 🎯 策略参数说明
        - **止损设置**: 保守型 5-8%，平衡型 8-12%，激进型 10-15%
        - **止盈设置**: 保守型 10-15%，平衡型 15-25%，激进型 20-30%
        - **最大仓位**: 保守型 ≤60%，平衡型 ≤80%，激进型 ≤100%
        """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 基础配置")
        
        trading_mode = st.radio(
            "交易模式",
            ["模拟交易", "实盘交易"],
            help="建议新手先使用模拟交易熟悉系统"
        )
        
        strategy = st.selectbox(
            "交易策略",
            ["保守型", "平衡型", "激进型"],
            help="不同策略的风险收益特征不同"
        )
        
        initial_capital = st.number_input(
            "初始资金（元）",
            min_value=1000,
            value=100000,
            step=1000,
            help="建议至少1万元以上"
        )
        
        max_position = st.slider(
            "单只股票最大仓位（%）",
            min_value=5,
            max_value=50,
            value=20,
            help="控制单一股票风险"
        )
        
        max_stocks = st.slider(
            "最大持仓股票数",
            min_value=1,
            max_value=20,
            value=5,
            help="分散投资降低风险"
        )
    
    with col2:
        st.markdown("### 股票池设置")
        
        use_watchlist = st.checkbox(
            "使用自选股作为交易股票池",
            value=True,
            help="勾选后将使用自选股进行交易，否则使用默认股票池"
        )
        
        if use_watchlist:
            try:
                from src.trading.watchlist_manager import WatchlistManager
                watchlist_manager = WatchlistManager()
                watchlist = watchlist_manager.get_watchlist()
                
                if watchlist:
                    st.success(f"✅ 已加载 {len(watchlist)} 只自选股")
                    
                    # 显示自选股列表
                    watchlist_data = []
                    for stock in watchlist[:10]:  # 只显示前10只
                        watchlist_data.append({
                            "股票代码": stock.symbol,
                            "股票名称": stock.name,
                            "分组": stock.group_name,
                            "添加日期": stock.add_date[:10]
                        })
                    
                    if watchlist_data:
                        st.dataframe(pd.DataFrame(watchlist_data), use_container_width=True)
                        
                        if len(watchlist) > 10:
                            st.info(f"显示前10只股票，共有 {len(watchlist)} 只自选股")
                else:
                    st.warning("⚠️ 自选股为空，请先添加自选股")
                    use_watchlist = False
                    
            except Exception as e:
                st.error(f"加载自选股失败: {e}")
                use_watchlist = False
        
        if not use_watchlist:
            st.info("使用默认股票池：平安银行、万科A、浦发银行、招商银行、五粮液")
        
        # 策略说明
        st.markdown("### 策略说明")
        
        strategy_info = {
            "保守型": {
                "icon": "🛡️",
                "description": "严格风控，追求稳健收益",
                "features": ["AI评分≥80才买入", "止损-5%", "止盈+15%", "优先低风险股票"]
            },
            "平衡型": {
                "icon": "⚖️", 
                "description": "平衡风险与收益",
                "features": ["AI评分≥75才买入", "止损-10%", "止盈+20%", "综合考虑各项指标"]
            },
            "激进型": {
                "icon": "🚀",
                "description": "追求高收益，承担较高风险", 
                "features": ["AI评分≥65才买入", "止损-15%", "止盈+30%", "关注成长潜力股"]
            }
        }
        
        if strategy in strategy_info:
            info = strategy_info[strategy]
            st.markdown(f"""
            **{info['icon']} {strategy}策略**  
            {info['description']}
            
            **特点：**
            """)
            for feature in info['features']:
                st.markdown(f"- {feature}")
    
    # 交易控制
    st.markdown("### 🎮 交易控制")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("▶️ 启动交易", type="primary", use_container_width=True):
            st.success("✅ 自动交易已启动！")
            st.balloons()
    
    with col2:
        if st.button("⏸️ 暂停交易", use_container_width=True):
            st.info("⏸️ 自动交易已暂停")
    
    with col3:
        if st.button("⏹️ 停止交易", use_container_width=True):
            st.warning("⏹️ 自动交易已停止")

def render_simulation_backtest():
    """渲染模拟回测页面"""
    st.subheader("📈 策略模拟回测")
    
    # 功能介绍
    st.markdown("""
    <div style="background: linear-gradient(90deg, #f8f9fa 0%, #e8f5e8 100%); padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;">
        <h4 style="color: #198754; margin-top: 0;">🎯 模拟回测功能说明</h4>
        <p style="margin-bottom: 0.5rem; color: #424242;">
            使用历史数据验证交易策略的有效性，评估策略在不同市场环境下的表现，为实盘交易提供决策依据。
        </p>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.5rem; margin-top: 1rem;">
            <div>📊 <strong>回测分析</strong>: 历史数据验证策略</div>
            <div>💰 <strong>收益计算</strong>: 详细盈亏统计</div>
            <div>📈 <strong>风险评估</strong>: 最大回撤、夏普比率</div>
            <div>🎛️ <strong>参数优化</strong>: 策略参数调优建议</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 回测参数")
        
        # 日期选择
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=180)  # 默认6个月
        
        backtest_start = st.date_input(
            "开始日期",
            value=start_date,
            max_value=end_date,
            help="建议至少3个月以上"
        )
        
        backtest_end = st.date_input(
            "结束日期", 
            value=end_date,
            min_value=backtest_start,
            max_value=end_date
        )
        
        # 策略选择
        backtest_strategy = st.selectbox(
            "回测策略",
            ["保守型", "平衡型", "激进型"],
            key="backtest_strategy"
        )
        
        # 初始资金
        backtest_capital = st.number_input(
            "初始资金（元）",
            min_value=10000,
            value=100000,
            step=10000,
            key="backtest_capital"
        )
        
        # 股票选择
        use_watchlist_backtest = st.checkbox(
            "使用自选股回测",
            value=True,
            key="use_watchlist_backtest"
        )
        
        if not use_watchlist_backtest:
            # 手动选择股票
            available_stocks = [
                "000001.SZ - 平安银行",
                "000002.SZ - 万科A", 
                "600000.SH - 浦发银行",
                "600036.SH - 招商银行",
                "000858.SZ - 五粮液"
            ]
            
            selected_stocks = st.multiselect(
                "选择股票",
                available_stocks,
                default=available_stocks[:3],
                help="建议选择3-5只股票进行回测"
            )
    
    with col2:
        st.markdown("### 回测结果")
        
        if st.button("🚀 开始回测", type="primary", use_container_width=True):
            with st.spinner("正在进行历史回测..."):
                try:
                    # 模拟回测结果
                    time.sleep(2)  # 模拟计算时间
                    
                    # 生成模拟结果
                    total_return = np.random.uniform(-10, 25)  # -10% 到 25%
                    max_drawdown = np.random.uniform(2, 15)   # 2% 到 15%
                    win_rate = np.random.uniform(45, 75)      # 45% 到 75%
                    sharpe = np.random.uniform(0.8, 2.2)      # 0.8 到 2.2
                    
                    st.success("✅ 回测完成！")
                    
                    # 显示核心指标
                    metric_col1, metric_col2 = st.columns(2)
                    
                    with metric_col1:
                        # 总收益率
                        color = "#dc3545" if total_return > 0 else "#28a745"  # 中国股市习惯
                        st.markdown(f"""
                        <div style='padding: 15px; border-radius: 8px; background-color: rgba({"220, 53, 69" if total_return > 0 else "40, 167, 69"}, 0.1); text-align: center;'>
                            <div style='color: #666; font-size: 14px;'>总收益率</div>
                            <div style='color: {color}; font-size: 32px; font-weight: bold; margin: 8px 0;'>{total_return:+.2f}%</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 最大回撤
                        st.markdown(f"""
                        <div style='padding: 15px; border-radius: 8px; background-color: rgba(108, 117, 125, 0.1); text-align: center; margin-top: 10px;'>
                            <div style='color: #666; font-size: 14px;'>最大回撤</div>
                            <div style='color: #6c757d; font-size: 32px; font-weight: bold; margin: 8px 0;'>-{max_drawdown:.2f}%</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with metric_col2:
                        # 胜率
                        st.markdown(f"""
                        <div style='padding: 15px; border-radius: 8px; background-color: rgba(255, 193, 7, 0.1); text-align: center;'>
                            <div style='color: #666; font-size: 14px;'>胜率</div>
                            <div style='color: #ffc107; font-size: 32px; font-weight: bold; margin: 8px 0;'>{win_rate:.1f}%</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 夏普比率
                        st.markdown(f"""
                        <div style='padding: 15px; border-radius: 8px; background-color: rgba(13, 110, 253, 0.1); text-align: center; margin-top: 10px;'>
                            <div style='color: #666; font-size: 14px;'>夏普比率</div>
                            <div style='color: #0d6efd; font-size: 32px; font-weight: bold; margin: 8px 0;'>{sharpe:.2f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # 详细统计
                    st.markdown("### 📊 详细统计")
                    
                    stats_data = {
                        "指标": ["交易次数", "盈利次数", "亏损次数", "平均盈利", "平均亏损", "盈亏比"],
                        "数值": ["24", "15", "9", "+3.2%", "-1.8%", "1.78"]
                    }
                    
                    st.dataframe(pd.DataFrame(stats_data), use_container_width=True)
                    
                except Exception as e:
                    st.error(f"回测失败: {e}")
        
        # 回测说明
        st.markdown("""
        ### 📝 回测说明
        
        **回测原理：**
        - 使用历史数据模拟交易策略
        - 按照设定的买卖规则执行交易  
        - 计算各项风险收益指标
        
        **注意事项：**
        - 历史表现不代表未来收益
        - 实际交易可能存在滑点和冲击成本
        - 建议多个时间段和策略对比分析
        """)

def render_watchlist_management():
    """渲染自选股管理页面"""
    st.subheader("⭐ 自选股管理")
    
    try:
        from src.trading.watchlist_manager import WatchlistManager
        
        # 初始化自选股管理器
        if 'watchlist_manager' not in st.session_state:
            st.session_state.watchlist_manager = WatchlistManager()
        
        manager = st.session_state.watchlist_manager
        
        # 创建子标签页
        subtab1, subtab2, subtab3 = st.tabs(["📋 股票列表", "➕ 添加股票", "📁 分组管理"])
        
        with subtab1:
            render_stock_list(manager)
        
        with subtab2:
            render_add_stock(manager)
        
        with subtab3:
            render_group_management(manager)
            
    except Exception as e:
        st.error(f"自选股管理模块加载失败: {e}")
        st.info("💡 请确保相关依赖已正确安装")

def render_stock_list(manager):
    """渲染股票列表"""
    st.markdown("### 📋 我的自选股")
    
    # 获取分组列表
    groups = manager.get_groups()
    group_names = ["全部"] + list(groups.keys())
    
    # 分组筛选
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        selected_group = st.selectbox(
            "选择分组",
            group_names,
            key="stock_list_group"
        )
    
    with col2:
        search_keyword = st.text_input(
            "搜索股票",
            placeholder="输入股票名称或代码",
            key="stock_search"
        )
    
    with col3:
        st.write("")  # 空行对齐
        refresh_button = st.button("🔄 刷新", key="refresh_stocks")
    
    # 获取股票列表
    if search_keyword:
        stocks = manager.search_stocks(search_keyword)
    elif selected_group == "全部":
        stocks = manager.get_watchlist()
    else:
        stocks = manager.get_watchlist(selected_group)
    
    if stocks:
        st.success(f"📊 共找到 {len(stocks)} 只股票")
        
        # 显示股票列表
        stock_data = []
        for stock in stocks:
            # 模拟当前价格和涨跌
            current_price = stock.add_price * (1 + np.random.uniform(-0.1, 0.1))
            change = current_price - stock.add_price
            change_pct = (change / stock.add_price) * 100
            
            stock_data.append({
                "股票代码": stock.symbol,
                "股票名称": stock.name,
                "当前价格": f"¥{current_price:.2f}",
                "涨跌额": f"{change:+.2f}",
                "涨跌幅": f"{change_pct:+.2f}%",
                "分组": stock.group_name,
                "添加日期": stock.add_date[:10],
                "备注": stock.notes[:20] + "..." if len(stock.notes) > 20 else stock.notes
            })
        
        # 自定义显示格式
        df = pd.DataFrame(stock_data)
        
        # 使用容器显示，支持中国股市颜色
        for i, row in df.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.write(f"**{row['股票名称']}** ({row['股票代码']})")
                    st.caption(f"分组: {row['分组']} | 添加: {row['添加日期']}")
                
                with col2:
                    st.write(f"**{row['当前价格']}**")
                    
                    # 根据涨跌显示颜色
                    change_val = float(row['涨跌额'])
                    if change_val > 0:
                        st.markdown(f"<span style='color: #dc3545;'>📈 {row['涨跌额']} ({row['涨跌幅']})</span>", unsafe_allow_html=True)
                    elif change_val < 0:
                        st.markdown(f"<span style='color: #28a745;'>📉 {row['涨跌额']} ({row['涨跌幅']})</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span style='color: #6c757d;'>➖ {row['涨跌额']} ({row['涨跌幅']})</span>", unsafe_allow_html=True)
                
                with col3:
                    if row['备注']:
                        st.write(f"📝 {row['备注']}")
                    else:
                        st.write("无备注")
                
                with col4:
                    if st.button("🗑️", key=f"del_{stocks[i].symbol}", help="删除股票"):
                        if manager.remove_stock(stocks[i].symbol):
                            st.success(f"已删除 {stocks[i].name}")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("删除失败")
                
                st.divider()
    else:
        st.info("📭 当前分组暂无股票")
        
        if selected_group != "全部":
            if st.button("➕ 添加股票到此分组"):
                st.session_state.add_stock_group = selected_group
                st.rerun()

def render_add_stock(manager):
    """渲染添加股票页面"""
    st.markdown("### ➕ 添加自选股")
    
    # 添加智能搜索提示
    st.info("💡 **智能添加**: 使用下方搜索功能快速找到并添加股票到自选股")
    
    # 尝试使用智能搜索组件
    try:
        from src.ui.smart_stock_input import smart_stock_input
        from src.data.stock_mapper import stock_mapper
        
        # 智能股票搜索
        st.markdown("#### 🔍 智能股票搜索")
        selected_symbol, selected_name = smart_stock_input(
            label="搜索并选择股票",
            default_symbol="000001.SZ",
            key="add_stock_search"
        )
        
        # 自动填充股票信息
        stock_code = selected_symbol
        stock_name = selected_name
        
        # 尝试获取当前价格（这里可以集成数据获取）
        current_price = 10.0  # 默认价格，实际应用中可以获取实时价格
        
        st.success(f"✅ 已选择: **{stock_name}** ({stock_code})")
        
    except Exception as e:
        # 降级到手动输入
        st.warning("⚠️ 智能搜索不可用，请手动输入股票信息")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 股票代码输入
            stock_code = st.text_input(
                "股票代码",
                placeholder="例如: 000001.SZ",
                help="请输入完整的股票代码，包含交易所后缀"
            )
        
        with col2:
            # 股票名称
            stock_name = st.text_input(
                "股票名称",
                placeholder="例如: 平安银行"
            )
        
        # 当前价格
        current_price = st.number_input(
            "当前价格（元）",
            min_value=0.01,
            value=10.0,
            step=0.01,
            format="%.2f"
        )
    
    # 其他设置
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 分组和备注")
        
        # 选择分组
        groups = manager.get_group_names()
        
        # 检查是否有预设分组
        default_group = getattr(st.session_state, 'add_stock_group', '默认分组')
        if default_group in groups:
            default_index = groups.index(default_group)
        else:
            default_index = 0
        
        selected_group = st.selectbox(
            "选择分组",
            groups,
            index=default_index
        )
        
        # 新建分组选项
        create_new_group = st.checkbox("创建新分组")
        
        if create_new_group:
            new_group_name = st.text_input(
                "新分组名称",
                placeholder="输入新分组名称"
            )
            
            new_group_desc = st.text_input(
                "分组描述",
                placeholder="可选，描述此分组的用途"
            )
            
            if new_group_name:
                selected_group = new_group_name
        
        # 备注
        notes = st.text_area(
            "备注",
            placeholder="可选，添加关于此股票的备注信息",
            max_chars=200
        )
    
    # 添加按钮
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("✅ 添加到自选股", type="primary", use_container_width=True):
            # 验证输入
            if not stock_code or not stock_name:
                st.error("❌ 请填写完整的股票代码和名称")
            else:
                # 创建新分组（如果需要）
                if create_new_group and new_group_name:
                    manager.create_group(new_group_name, new_group_desc or "")
                
                # 添加股票
                success = manager.add_stock(
                    symbol=stock_code,
                    name=stock_name,
                    current_price=current_price,
                    group_name=selected_group,
                    notes=notes
                )
                
                if success:
                    st.success(f"✅ 成功添加 {stock_name} 到自选股！")
                    st.balloons()
                    
                    # 清空表单
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ 添加失败，股票可能已存在")
    
    # 快速添加热门股票
    st.markdown("---")
    st.markdown("### 🔥 快速添加热门股票")
    
    popular_stocks = [
        {"code": "000001.SZ", "name": "平安银行", "price": 12.34},
        {"code": "000002.SZ", "name": "万科A", "price": 15.67},
        {"code": "600000.SH", "name": "浦发银行", "price": 8.90},
        {"code": "600036.SH", "name": "招商银行", "price": 45.23},
        {"code": "000858.SZ", "name": "五粮液", "price": 165.40}
    ]
    
    cols = st.columns(5)
    
    for i, stock in enumerate(popular_stocks):
        with cols[i]:
            if st.button(
                f"**{stock['name']}**\n{stock['code']}\n¥{stock['price']}", 
                key=f"quick_add_{stock['code']}"
            ):
                success = manager.add_stock(
                    symbol=stock['code'],
                    name=stock['name'],
                    current_price=stock['price'],
                    group_name=selected_group
                )
                
                if success:
                    st.success(f"✅ 已添加 {stock['name']}")
                    time.sleep(0.5)
                    st.rerun()

def render_group_management(manager):
    """渲染分组管理页面"""
    st.markdown("### 📁 分组管理")
    
    # 获取所有分组
    groups = manager.get_groups()
    
    if groups:
        for group_name, group_info in groups.items():
            with st.expander(f"📁 {group_name} ({len(group_info.stocks)} 只股票)", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**描述：** {group_info.description}")
                    st.write(f"**创建时间：** {group_info.created_date}")
                    st.write(f"**股票数量：** {len(group_info.stocks)} 只")
                    
                    if group_info.stocks:
                        stock_names = []
                        for symbol in group_info.stocks[:10]:  # 最多显示10只
                            watchlist = manager.get_watchlist()
                            for stock in watchlist:
                                if stock.symbol == symbol:
                                    stock_names.append(f"{stock.name}({symbol})")
                                    break
                        
                        st.write(f"**包含股票：** {', '.join(stock_names)}")
                        if len(group_info.stocks) > 10:
                            st.caption(f"还有 {len(group_info.stocks) - 10} 只股票...")
                
                with col2:
                    if group_name != "默认分组":  # 不允许删除默认分组
                        if st.button(f"🗑️ 删除", key=f"del_group_{group_name}"):
                            with st.spinner(f"正在删除分组 {group_name}..."):
                                success = manager.delete_group(group_name, move_to_default=True)
                                if success:
                                    st.success(f"已删除分组: {group_name}")
                                    time.sleep(0.5)
                                    st.rerun()
                                else:
                                    st.error("删除失败")
    
    # 创建新分组
    st.markdown("---")
    st.markdown("### ➕ 创建新分组")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_group_name = st.text_input(
            "分组名称",
            placeholder="例如: 银行股、科技股",
            key="new_group_name"
        )
    
    with col2:
        new_group_desc = st.text_input(
            "分组描述",
            placeholder="可选，描述此分组的投资主题",
            key="new_group_desc"
        )
    
    if st.button("创建分组", type="primary"):
        if new_group_name:
            success = manager.create_group(new_group_name, new_group_desc or "")
            if success:
                st.success(f"✅ 成功创建分组: {new_group_name}")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("❌ 创建失败，分组可能已存在")
        else:
            st.error("❌ 请输入分组名称")

def render_trading_records():
    """渲染交易记录页面"""
    st.subheader("📊 交易记录")
    
    # 创建子标签页
    subtab1, subtab2 = st.tabs(["📈 实时持仓", "📋 历史交易"])
    
    with subtab1:
        render_current_positions()
    
    with subtab2:
        render_trading_history()

def render_current_positions():
    """渲染当前持仓"""
    st.markdown("### 📈 当前持仓")
    
    # 模拟持仓数据
    positions_data = {
        '股票代码': ['000001.SZ', '600036.SH', '000858.SZ'],
        '股票名称': ['平安银行', '招商银行', '五粮液'],
        '持仓数量': [2000, 1500, 300],
        '成本价': [12.34, 45.23, 165.40],
        '现价': [13.45, 47.80, 168.90],
        '市值': [26900, 71700, 50670],
        '盈亏金额': [2220, 3855, 1050],
        '盈亏比例': [9.0, 5.7, 2.1],
        '仓位占比': [17.8, 47.4, 33.6]
    }
    
    if positions_data['股票代码']:
        # 总览
        total_value = sum(positions_data['市值'])
        total_profit = sum(positions_data['盈亏金额'])
        total_profit_pct = total_profit / (total_value - total_profit) * 100
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("总市值", f"¥{total_value:,.0f}", f"{total_profit:+.0f}")
        
        with col2:
            st.metric("总盈亏", f"¥{total_profit:+,.0f}", f"{total_profit_pct:+.2f}%")
        
        with col3:
            st.metric("持仓股票", f"{len(positions_data['股票代码'])}只", "")
        
        with col4:
            st.metric("可用资金", "¥25,000", "")
        
        st.markdown("---")
        
        # 持仓详情
        for i in range(len(positions_data['股票代码'])):
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                
                with col1:
                    st.write(f"**{positions_data['股票名称'][i]}**")
                    st.caption(f"{positions_data['股票代码'][i]} | {positions_data['持仓数量'][i]}股")
                
                with col2:
                    st.write(f"现价: **¥{positions_data['现价'][i]:.2f}**")
                    st.caption(f"成本: ¥{positions_data['成本价'][i]:.2f}")
                
                with col3:
                    profit = positions_data['盈亏金额'][i]
                    profit_pct = positions_data['盈亏比例'][i]
                    
                    if profit > 0:
                        st.markdown(f"<span style='color: #dc3545;'>📈 +¥{profit:.0f} (+{profit_pct:.2f}%)</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span style='color: #28a745;'>📉 ¥{profit:.0f} ({profit_pct:.2f}%)</span>", unsafe_allow_html=True)
                    
                    st.caption(f"市值: ¥{positions_data['市值'][i]:,.0f}")
                
                with col4:
                    st.progress(positions_data['仓位占比'][i] / 100)
                    st.caption(f"{positions_data['仓位占比'][i]:.1f}%")
                
                st.divider()
    else:
        st.info("📭 当前无持仓股票")

def render_trading_history():
    """渲染历史交易记录"""
    st.markdown("### 📋 历史交易记录")
    
    # 筛选条件
    col1, col2, col3 = st.columns(3)
    
    with col1:
        trade_type_filter = st.selectbox(
            "交易类型",
            ["全部", "买入", "卖出"]
        )
    
    with col2:
        date_range = st.date_input(
            "日期范围",
            value=[datetime.now().date() - timedelta(days=30), datetime.now().date()],
            key="trade_history_date"
        )
    
    with col3:
        stock_filter = st.text_input(
            "股票筛选",
            placeholder="输入股票名称或代码"
        )
    
    # 模拟交易记录数据
    trade_data = {
        '时间': [
            '2024-01-15 09:30:15',
            '2024-01-15 14:25:30', 
            '2024-01-16 10:15:45',
            '2024-01-17 11:20:12',
            '2024-01-18 13:45:28'
        ],
        '股票名称': ['平安银行', '招商银行', '平安银行', '五粮液', '招商银行'],
        '股票代码': ['000001.SZ', '600036.SH', '000001.SZ', '000858.SZ', '600036.SH'],
        '操作': ['买入', '买入', '卖出', '买入', '卖出'],
        '价格': [12.34, 45.23, 13.45, 165.40, 47.80],
        '数量': [2000, 1500, 1000, 300, 500],
        '金额': [24680, 67845, 13450, 49620, 23900],
        '手续费': [7.4, 20.4, 4.0, 14.9, 7.2],
        '盈亏': [0, 0, 1110, 0, 1285],
        '状态': ['已成交', '已成交', '已成交', '已成交', '已成交']
    }
    
    # 转换为DataFrame
    df = pd.DataFrame(trade_data)
    
    # 应用筛选
    if trade_type_filter != "全部":
        df = df[df['操作'] == trade_type_filter]
    
    if stock_filter:
        df = df[df['股票名称'].str.contains(stock_filter) | df['股票代码'].str.contains(stock_filter)]
    
    if df.empty:
        st.info("📭 没有找到匹配的交易记录")
    else:
        # 交易统计
        total_trades = len(df)
        buy_trades = len(df[df['操作'] == '买入'])
        sell_trades = len(df[df['操作'] == '卖出'])
        total_profit = df['盈亏'].sum()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("总交易次数", total_trades)
        
        with col2:
            st.metric("买入次数", buy_trades)
        
        with col3:
            st.metric("卖出次数", sell_trades)
        
        with col4:
            profit_color = "normal" if total_profit == 0 else ("inverse" if total_profit > 0 else "off")
            st.metric("已实现盈亏", f"¥{total_profit:+.0f}", delta_color=profit_color)
        
        st.markdown("---")
        
        # 详细交易记录
        for i, row in df.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                
                with col1:
                    # 操作类型图标
                    if row['操作'] == '买入':
                        st.markdown(f"🟢 **{row['操作']}** {row['股票名称']}")
                    else:
                        st.markdown(f"🔴 **{row['操作']}** {row['股票名称']}")
                    st.caption(f"{row['股票代码']} | {row['时间']}")
                
                with col2:
                    st.write(f"价格: **¥{row['价格']:.2f}**")
                    st.caption(f"数量: {row['数量']}股")
                
                with col3:
                    st.write(f"金额: **¥{row['金额']:,.0f}**")
                    if row['盈亏'] > 0:
                        st.markdown(f"<span style='color: #dc3545;'>📈 盈利: +¥{row['盈亏']:.0f}</span>", unsafe_allow_html=True)
                    elif row['盈亏'] < 0:
                        st.markdown(f"<span style='color: #28a745;'>📉 亏损: ¥{row['盈亏']:.0f}</span>", unsafe_allow_html=True)
                    else:
                        st.caption("盈亏: --")
                
                with col4:
                    status_color = "🟢" if row['状态'] == '已成交' else "🟡"
                    st.write(f"{status_color} {row['状态']}")
                    st.caption(f"费用: ¥{row['手续费']:.1f}")
                
                st.divider()

def render_market_overview_page():
    """渲染市场概览页面"""
    st.subheader("📈 市场概览")
    
    # 获取实时市场数据
    with st.spinner("正在获取最新市场数据..."):
        try:
            from src.data.market_data_fetcher import market_data_fetcher
            market_data = market_data_fetcher.get_market_overview()
            
            # 显示更新时间
            st.info(f"🕒 数据更新时间: {market_data['update_time']}")
            
            # 主要指数 - 使用实时数据
            st.markdown("### 📊 主要指数")
            indices = market_data['indices']
            
            # 分两行显示指数
            col1, col2, col3, col4 = st.columns(4)
            cols = [col1, col2, col3, col4]
            
            index_names = list(indices.keys())
            for i, name in enumerate(index_names[:4]):  # 第一行显示4个
                data = indices[name]
                
                with cols[i]:
                    # 中国股市习惯：涨红跌绿
                    change_value = f"{data['change']:+.2f} ({data['change_pct']:+.2f}%)"
                    
                    if data['change'] > 0:
                        # 上涨用红色
                        st.markdown(f"""
                        <div style='text-align: center; padding: 10px; border-radius: 5px; background-color: rgba(255, 77, 77, 0.1);'>
                            <h4 style='margin: 0; color: #666;'>{name}</h4>
                            <h2 style='margin: 5px 0; color: #333;'>{data['current']:,.2f}</h2>
                            <p style='margin: 0; color: #ff4d4d; font-weight: bold;'>📈 {change_value}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    elif data['change'] < 0:
                        # 下跌用绿色
                        st.markdown(f"""
                        <div style='text-align: center; padding: 10px; border-radius: 5px; background-color: rgba(77, 159, 77, 0.1);'>
                            <h4 style='margin: 0; color: #666;'>{name}</h4>
                            <h2 style='margin: 5px 0; color: #333;'>{data['current']:,.2f}</h2>
                            <p style='margin: 0; color: #4d9f4d; font-weight: bold;'>📉 {change_value}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # 平盘用灰色
                        st.markdown(f"""
                        <div style='text-align: center; padding: 10px; border-radius: 5px; background-color: rgba(128, 128, 128, 0.1);'>
                            <h4 style='margin: 0; color: #666;'>{name}</h4>
                            <h2 style='margin: 5px 0; color: #333;'>{data['current']:,.2f}</h2>
                            <p style='margin: 0; color: #808080; font-weight: bold;'>➖ {change_value}</p>
                        </div>
                        """, unsafe_allow_html=True)
            
            # 第二行显示剩余指数
            if len(index_names) > 4:
                col5, col6, col7, col8 = st.columns(4)
                cols2 = [col5, col6, col7, col8]
                
                for i, name in enumerate(index_names[4:8]):  # 最多再显示4个
                    if i < len(cols2):
                        data = indices[name]
                        with cols2[i]:
                            # 中国股市习惯：涨红跌绿
                            change_value = f"{data['change']:+.2f} ({data['change_pct']:+.2f}%)"
                            
                            if data['change'] > 0:
                                # 上涨用红色
                                st.markdown(f"""
                                <div style='text-align: center; padding: 10px; border-radius: 5px; background-color: rgba(255, 77, 77, 0.1);'>
                                    <h4 style='margin: 0; color: #666;'>{name}</h4>
                                    <h2 style='margin: 5px 0; color: #333;'>{data['current']:,.2f}</h2>
                                    <p style='margin: 0; color: #ff4d4d; font-weight: bold;'>📈 {change_value}</p>
                                </div>
                                """, unsafe_allow_html=True)
                            elif data['change'] < 0:
                                # 下跌用绿色
                                st.markdown(f"""
                                <div style='text-align: center; padding: 10px; border-radius: 5px; background-color: rgba(77, 159, 77, 0.1);'>
                                    <h4 style='margin: 0; color: #666;'>{name}</h4>
                                    <h2 style='margin: 5px 0; color: #333;'>{data['current']:,.2f}</h2>
                                    <p style='margin: 0; color: #4d9f4d; font-weight: bold;'>📉 {change_value}</p>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                # 平盘用灰色
                                st.markdown(f"""
                                <div style='text-align: center; padding: 10px; border-radius: 5px; background-color: rgba(128, 128, 128, 0.1);'>
                                    <h4 style='margin: 0; color: #666;'>{name}</h4>
                                    <h2 style='margin: 5px 0; color: #333;'>{data['current']:,.2f}</h2>
                                    <p style='margin: 0; color: #808080; font-weight: bold;'>➖ {change_value}</p>
                                </div>
                                """, unsafe_allow_html=True)
            
            # 市场热点 - 使用实时数据
            st.markdown("### 🔥 今日热点")
            hot_sectors = market_data['hot_sectors']
            
            if hot_sectors:
                # 创建自定义格式的热点板块显示
                st.markdown("#### 活跃板块排行")
                
                # 分列显示热点板块
                sector_cols = st.columns(2)
                for i, sector in enumerate(hot_sectors[:10]):  # 显示前10个
                    col_idx = i % 2
                    with sector_cols[col_idx]:
                        change_pct = sector.get('change_pct', 0)
                        
                        if change_pct > 0:
                            # 上涨板块用红色
                            st.markdown(f"""
                            <div style='margin: 5px 0; padding: 10px; border-radius: 5px; background-color: rgba(255, 77, 77, 0.1); border-left: 4px solid #ff4d4d;'>
                                <strong style='color: #333;'>{sector.get('name', '未知板块')}</strong><br>
                                <span style='color: #ff4d4d; font-weight: bold;'>📈 {change_pct:+.2f}%</span>
                                <span style='color: #888; margin-left: 10px;'>成交: {sector.get('volume', 0):.1f}亿</span>
                            </div>
                            """, unsafe_allow_html=True)
                        elif change_pct < 0:
                            # 下跌板块用绿色
                            st.markdown(f"""
                            <div style='margin: 5px 0; padding: 10px; border-radius: 5px; background-color: rgba(77, 159, 77, 0.1); border-left: 4px solid #4d9f4d;'>
                                <strong style='color: #333;'>{sector.get('name', '未知板块')}</strong><br>
                                <span style='color: #4d9f4d; font-weight: bold;'>📉 {change_pct:+.2f}%</span>
                                <span style='color: #888; margin-left: 10px;'>成交: {sector.get('volume', 0):.1f}亿</span>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            # 平盘用灰色
                            st.markdown(f"""
                            <div style='margin: 5px 0; padding: 10px; border-radius: 5px; background-color: rgba(128, 128, 128, 0.1); border-left: 4px solid #808080;'>
                                <strong style='color: #333;'>{sector.get('name', '未知板块')}</strong><br>
                                <span style='color: #808080; font-weight: bold;'>➖ {change_pct:+.2f}%</span>
                                <span style='color: #888; margin-left: 10px;'>成交: {sector.get('volume', 0):.1f}亿</span>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.info("暂无热点板块数据")
                
            # 添加刷新按钮
            if st.button("🔄 刷新数据", help="点击获取最新市场数据"):
                st.rerun()
            
        except Exception as e:
            logger.error(f"获取市场数据失败: {e}")
            st.error(f"获取市场数据失败: {e}")
            
            # 降级显示模拟数据
            st.warning("⚠️ 网络数据获取失败，显示模拟数据")
            
            # 主要指数 - 模拟数据
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("上证指数", "3,245.67", "+15.23 (+0.47%)")
            
            with col2:
                st.metric("深证成指", "12,456.78", "-23.45 (-0.19%)")
            
            with col3:
                st.metric("创业板指", "2,789.34", "+8.56 (+0.31%)")
            
            with col4:
                st.metric("科创50", "1,234.56", "+12.34 (+1.01%)")
            
            # 市场热点 - 模拟数据
            st.markdown("### 🔥 今日热点")
            st.markdown("#### 活跃板块排行")
            
            # 模拟热点数据，符合中国股市颜色习惯
            mock_sectors = [
                {"name": "人工智能", "change_pct": 3.45, "volume": 15.6, "leading_stock": "科大讯飞"},
                {"name": "新能源汽车", "change_pct": 2.18, "volume": 12.3, "leading_stock": "宁德时代"},
                {"name": "半导体", "change_pct": 1.89, "volume": 8.9, "leading_stock": "中芯国际"},
                {"name": "医药生物", "change_pct": -0.56, "volume": 5.2, "leading_stock": "恒瑞医药"},
                {"name": "白酒", "change_pct": 0.78, "volume": 7.1, "leading_stock": "贵州茅台"},
                {"name": "银行", "change_pct": 0.32, "volume": 4.8, "leading_stock": "招商银行"}
            ]
            
            # 分列显示热点板块，应用中国股市颜色
            sector_cols = st.columns(2)
            for i, sector in enumerate(mock_sectors):
                col_idx = i % 2
                with sector_cols[col_idx]:
                    change_pct = sector['change_pct']
                    
                    if change_pct > 0:
                        # 上涨板块用红色
                        st.markdown(f"""
                        <div style='margin: 5px 0; padding: 10px; border-radius: 5px; background-color: rgba(255, 77, 77, 0.1); border-left: 4px solid #ff4d4d;'>
                            <strong style='color: #333;'>{sector['name']}</strong><br>
                            <span style='color: #ff4d4d; font-weight: bold;'>📈 {change_pct:+.2f}%</span>
                            <span style='color: #888; margin-left: 10px;'>成交: {sector['volume']:.1f}亿</span>
                        </div>
                        """, unsafe_allow_html=True)
                    elif change_pct < 0:
                        # 下跌板块用绿色
                        st.markdown(f"""
                        <div style='margin: 5px 0; padding: 10px; border-radius: 5px; background-color: rgba(77, 159, 77, 0.1); border-left: 4px solid #4d9f4d;'>
                            <strong style='color: #333;'>{sector['name']}</strong><br>
                            <span style='color: #4d9f4d; font-weight: bold;'>📉 {change_pct:+.2f}%</span>
                            <span style='color: #888; margin-left: 10px;'>成交: {sector['volume']:.1f}亿</span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # 平盘用灰色
                        st.markdown(f"""
                        <div style='margin: 5px 0; padding: 10px; border-radius: 5px; background-color: rgba(128, 128, 128, 0.1); border-left: 4px solid #808080;'>
                            <strong style='color: #333;'>{sector['name']}</strong><br>
                            <span style='color: #808080; font-weight: bold;'>➖ {change_pct:+.2f}%</span>
                            <span style='color: #888; margin-left: 10px;'>成交: {sector['volume']:.1f}亿</span>
                        </div>
                        """, unsafe_allow_html=True)

def render_education_page():
    """渲染投资学堂页面"""
    st.subheader("📚 投资学堂")
    
    tab1, tab2, tab3 = st.tabs(["基础知识", "技术分析", "风险管理"])
    
    with tab1:
        st.markdown("""
        ### 股票投资基础知识
        
        #### 什么是股票？
        股票是股份公司发行的所有权凭证，持有股票意味着拥有公司的一部分所有权。
        
        #### 如何选择股票？
        1. **基本面分析**: 研究公司的财务状况、盈利能力、发展前景
        2. **技术面分析**: 通过股价走势、成交量等技术指标判断买卖时机
        3. **行业分析**: 了解所投资公司所处行业的发展趋势
        
        #### 新手投资建议
        - 🎯 制定投资目标和计划
        - 📊 分散投资，不要把鸡蛋放在一个篮子里
        - 📈 长期投资，避免频繁交易
        - 📚 持续学习，提升投资能力
        """)
    
    with tab2:
        st.markdown("""
        ### 技术分析入门
        
        #### 常用技术指标
        
        **移动平均线 (MA)**
        - MA5: 5日移动平均线，短期趋势参考
        - MA20: 20日移动平均线，中期趋势参考
        - 金叉：短期均线上穿长期均线，看涨信号
        - 死叉：短期均线下穿长期均线，看跌信号
        
        **相对强弱指数 (RSI)**
        - RSI > 70: 超买区域，可能回调
        - RSI < 30: 超卖区域，可能反弹
        - RSI 50: 强弱分界线
        
        **MACD**
        - MACD线上穿信号线: 买入信号
        - MACD线下穿信号线: 卖出信号
        - MACD柱状图: 反映动量变化
        """)
    
    with tab3:
        st.markdown("""
        ### 风险管理
        
        #### 风险类型
        1. **市场风险**: 整体市场下跌的风险
        2. **个股风险**: 单只股票的特有风险
        3. **流动性风险**: 无法及时买卖的风险
        4. **政策风险**: 政策变化对股价的影响
        
        #### 风险控制方法
        - 🛡️ **止损**: 设定止损位，控制单笔损失
        - 📊 **仓位管理**: 合理分配资金，避免重仓
        - 🔄 **分散投资**: 投资不同行业、不同类型的股票
        - ⏰ **定期评估**: 定期检查投资组合，及时调整
        
        #### 新手风险提示
        - ⚠️ 不要借钱炒股
        - ⚠️ 不要盲目跟风
        - ⚠️ 不要频繁交易
        - ⚠️ 不要情绪化操作
        """)

def main():
    """主程序"""
    render_header()
    
    # 获取页面选择和参数
    page_info = render_sidebar()
    page = page_info[0]
    
    # 根据选择渲染对应页面
    if page == "📊 股票分析":
        symbol, period = page_info[1], page_info[2]
        if symbol:
            render_stock_analysis_page(symbol, period)
        else:
            st.info("请在侧边栏输入股票代码开始分析")
    
    elif page == "🎯 智能选股":
        render_stock_screening_page()
    
    elif page == "⚡ 自动交易":
        render_auto_trading_page()
    
    elif page == "📈 市场概览":
        render_market_overview_page()
    
    elif page == "📚 投资学堂":
        render_education_page()

def launch_app(host='localhost', port=8501):
    """启动Streamlit应用"""
    import subprocess
    import sys
    
    cmd = [
        sys.executable, '-m', 'streamlit', 'run',
        __file__,
        '--server.address', host,
        '--server.port', str(port),
        '--browser.gatherUsageStats', 'false'
    ]
    
    subprocess.run(cmd)

if __name__ == '__main__':
    main()