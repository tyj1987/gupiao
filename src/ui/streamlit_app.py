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
    
    # 使用智能股票输入组件
    try:
        from src.ui.smart_stock_input import smart_stock_input, display_stock_info
        
        # 智能股票选择
        st.subheader("📊 股票分析")
        
        symbol, name = smart_stock_input(
            label="选择要分析的股票",
            default_symbol=symbol,
            key="stock_analysis"
        )
        
        # 显示股票信息卡片
        display_stock_info(symbol, name)
        
    except Exception as e:
        # 降级处理
        try:
            from src.data.stock_mapper import stock_mapper
            stock_name = stock_mapper.get_stock_name(symbol)
            display_title = f"{stock_name} ({symbol})" if stock_name != symbol else symbol
        except:
            display_title = symbol
        
        st.subheader(f"📊 股票分析: {display_title}")
    
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
        risk_class = f"risk-{risk_level.lower()}" if risk_level.lower() in ['low', 'medium', 'high'] else "risk-medium"
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
                                "upside": st.column_config.NumberColumn(
                                    "上涨空间",
                                    format="%.1f%%"
                                ),
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
                    df = pd.DataFrame(screening_results)
                    st.dataframe(df, hide_index=True, use_container_width=True)
                    
            except Exception as e:
                st.error(f"筛选过程中出现错误: {e}")
                logger.error(f"股票筛选错误: {e}")
                
                # 显示错误详情（仅在调试模式下）
                if st.checkbox("显示错误详情"):
                    st.code(str(e))

def render_auto_trading_page():
    """渲染自动交易页面"""
    st.subheader("⚡ 智能自动交易")
    
    st.warning("⚠️ 自动交易功能仅供学习和模拟使用，实盘交易请谨慎操作！")
    
    # 交易设置
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("交易配置")
        
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
            value=10000,
            step=1000
        )
        
        max_position = st.slider(
            "单只股票最大仓位（%）",
            min_value=5,
            max_value=50,
            value=20
        )
    
    with col2:
        st.subheader("交易统计")
        
        # 模拟交易统计
        col2_1, col2_2 = st.columns(2)
        
        with col2_1:
            st.metric("总收益率", "+12.5%", "+2.3%")
            st.metric("胜率", "68.5%", "+5.2%")
        
        with col2_2:
            st.metric("最大回撤", "-8.2%", "-1.1%")
            st.metric("夏普比率", "1.45", "+0.23")
    
    # 交易控制
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("▶️ 启动交易", type="primary"):
            st.success("自动交易已启动！")
    
    with col2:
        if st.button("⏸️ 暂停交易"):
            st.info("自动交易已暂停")
    
    with col3:
        if st.button("⏹️ 停止交易"):
            st.warning("自动交易已停止")
    
    # 交易日志
    st.subheader("📝 交易记录")
    
    # 模拟交易记录
    trade_data = {
        '时间': ['2024-01-15 09:30', '2024-01-15 14:25', '2024-01-16 10:15'],
        '股票': ['平安银行', '万科A', '平安银行'],
        '操作': ['买入', '买入', '卖出'],
        '价格': [12.34, 15.67, 13.45],
        '数量': [1000, 800, 1000],
        '金额': [12340, 12536, 13450],
        '状态': ['已成交', '已成交', '已成交']
    }
    
    trade_df = pd.DataFrame(trade_data)
    st.dataframe(trade_df, use_container_width=True)

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
                change_color = "normal" if data['change'] >= 0 else "inverse"
                
                with cols[i]:
                    st.metric(
                        name, 
                        f"{data['current']:,.2f}",
                        f"{data['change']:+.2f} ({data['change_pct']:+.2f}%)"
                    )
            
            # 第二行显示剩余指数
            if len(index_names) > 4:
                col5, col6, col7, col8 = st.columns(4)
                cols2 = [col5, col6, col7, col8]
                
                for i, name in enumerate(index_names[4:8]):  # 最多再显示4个
                    if i < len(cols2):
                        data = indices[name]
                        with cols2[i]:
                            st.metric(
                                name, 
                                f"{data['current']:,.2f}",
                                f"{data['change']:+.2f} ({data['change_pct']:+.2f}%)"
                            )
            
            # 市场热点 - 使用实时数据
            st.markdown("### 🔥 今日热点")
            hot_sectors = market_data['hot_sectors']
            
            if hot_sectors:
                df_hot = pd.DataFrame(hot_sectors)
                st.dataframe(df_hot, use_container_width=True)
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
            st.subheader("🔥 今日热点")
            
            hot_topics = [
                {"板块": "人工智能", "涨跌幅": "+3.45%", "领涨股": "科大讯飞", "资金流入": "15.6亿"},
                {"板块": "新能源汽车", "涨跌幅": "+2.18%", "领涨股": "宁德时代", "资金流入": "12.3亿"},
                {"板块": "半导体", "涨跌幅": "+1.89%", "领涨股": "中芯国际", "资金流入": "8.9亿"},
                {"板块": "医药生物", "涨跌幅": "-0.56%", "领涨股": "恒瑞医药", "资金流入": "5.2亿"}
            ]
            
            df_hot = pd.DataFrame(hot_topics)
            st.dataframe(df_hot, use_container_width=True)

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