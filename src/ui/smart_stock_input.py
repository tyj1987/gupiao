#!/usr/bin/env python3
"""
智能股票输入组件
"""

import streamlit as st
from typing import Optional, Tuple
from src.data.stock_mapper import stock_mapper

def smart_stock_input(
    label: str = "股票查询",
    default_symbol: str = "000001.SZ",
    key: str = "stock_input"
) -> Tuple[str, str]:
    """
    智能股票输入组件
    
    Args:
        label: 输入框标签
        default_symbol: 默认股票代码
        key: 组件唯一键
        
    Returns:
        Tuple[股票代码, 股票名称]
    """
    
    # 初始化session state
    session_key = f"{key}_selected_stock"
    if session_key not in st.session_state:
        # 查找默认股票的完整信息
        default_name = stock_mapper.get_stock_name(default_symbol)
        if default_name != default_symbol:
            st.session_state[session_key] = f"{default_symbol} - {default_name}"
        else:
            # 如果找不到默认股票，使用第一个可用的股票
            all_stocks = stock_mapper.get_all_stocks()
            if all_stocks:
                first_symbol, first_name = next(iter(all_stocks.items()))
                st.session_state[session_key] = f"{first_symbol} - {first_name}"
            else:
                st.session_state[session_key] = default_symbol
    
    # 获取所有股票选项
    all_stocks = stock_mapper.get_all_stocks()
    
    # 创建选项列表 (代码 - 名称)
    stock_options = []
    for symbol, name in sorted(all_stocks.items()):
        stock_options.append(f"{symbol} - {name}")
    
    # 找到当前选中的选项索引
    current_selection = st.session_state[session_key]
    current_index = 0
    if current_selection in stock_options:
        current_index = stock_options.index(current_selection)
    
    # 创建主要选择界面
    st.markdown(f"### {label}")
    
    # 方式1: 下拉选择框
    with st.container():
        selected_stock = st.selectbox(
            "选择股票",
            options=stock_options,
            index=current_index,
            key=f"{key}_main_select",
            help="从列表中选择股票，支持键盘输入快速搜索"
        )
        
        # 更新session state
        if selected_stock != st.session_state[session_key]:
            st.session_state[session_key] = selected_stock
    
    # 方式2: 智能搜索输入
    with st.expander("🔍 智能搜索", expanded=False):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            search_input = st.text_input(
                "输入股票代码或名称",
                placeholder="如: 中国银行, 601988, 中行, 茅台",
                key=f"{key}_search_input",
                help="支持股票代码、名称、简称搜索"
            )
        
        with col2:
            clear_search = st.button("清空", key=f"{key}_clear")
            if clear_search:
                st.rerun()
        
        if search_input.strip():
            # 实时搜索建议
            search_results = stock_mapper.search_stocks(search_input.strip(), limit=8)
            
            if search_results:
                st.markdown("**搜索结果:**")
                
                # 使用列布局显示搜索结果
                num_cols = min(2, len(search_results))
                cols = st.columns(num_cols)
                
                for i, result in enumerate(search_results):
                    col_idx = i % num_cols
                    with cols[col_idx]:
                        result_key = f"{key}_result_{result['symbol']}"
                        button_text = f"📊 {result['name']}\n`{result['symbol']}`"
                        
                        if st.button(
                            button_text,
                            key=result_key,
                            help=f"选择 {result['name']} ({result['symbol']})",
                            use_container_width=True
                        ):
                            # 用户点击了搜索结果
                            new_selection = f"{result['symbol']} - {result['name']}"
                            st.session_state[session_key] = new_selection
                            st.success(f"✅ 已选择: **{result['name']}** ({result['symbol']})")
                            st.rerun()
            else:
                st.warning(f"🔍 未找到匹配的股票: `{search_input}`")
                st.info("💡 尝试输入:")
                st.markdown("- 股票代码: `000001`, `600519.SH`")
                st.markdown("- 股票名称: `平安银行`, `贵州茅台`") 
                st.markdown("- 常用简称: `中行`, `工行`, `茅台`")
    
    # 解析最终选择的股票
    final_selection = st.session_state[session_key]
    if " - " in final_selection:
        symbol, name = final_selection.split(" - ", 1)
    else:
        symbol = final_selection
        name = stock_mapper.get_stock_name(symbol)
    
    return symbol.strip(), name.strip()

def display_stock_info(symbol: str, name: str):
    """显示股票信息卡片"""
    
    # 判断市场
    if symbol.endswith('.SZ') or symbol.endswith('.SH'):
        market = "🇨🇳 A股"
        market_class = "china-stock"
    else:
        market = "🇺🇸 美股"
        market_class = "us-stock"
    
    # 显示股票信息
    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
    ">
        <h4 style="margin: 0; color: #495057;">
            📊 {name} 
            <span style="color: #6c757d; font-size: 0.8em;">({symbol})</span>
        </h4>
        <p style="margin: 0.5rem 0 0 0; color: #6c757d;">
            {market} | 代码: {symbol}
        </p>
    </div>
    """, unsafe_allow_html=True)
