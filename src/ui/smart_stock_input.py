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
    
    # 添加搜索模式选择
    search_mode = st.radio(
        "搜索方式",
        ["🔍 智能搜索", "📋 列表选择"],
        index=0,
        horizontal=True,
        key=f"{key}_search_mode",
        help="智能搜索支持模糊搜索，列表选择支持完整浏览"
    )
    
    if search_mode == "🔍 智能搜索":
        # 方式1: 智能搜索输入（现在作为主要方式）
        col1, col2 = st.columns([4, 1])
        
        with col1:
            search_input = st.text_input(
                "输入股票代码或名称进行搜索",
                placeholder="如: 中国银行, 601988, 中行, 茅台, 平安",
                key=f"{key}_search_input",
                help="🔍 支持股票代码、完整名称、简称模糊搜索"
            )
        
        with col2:
            st.write("")  # 空行对齐
            clear_search = st.button("🗑️ 清空", key=f"{key}_clear")
            if clear_search:
                st.rerun()
        
        # 显示搜索提示
        if not search_input.strip():
            st.info("💡 **搜索提示**: 可以输入股票代码(如: 000001)、完整名称(如: 平安银行)或简称(如: 中行)")
            
            # 显示常用股票快速选择
            st.markdown("**🔥 热门股票快速选择:**")
            popular_stocks = [
                ("000001.SZ", "平安银行"),
                ("600036.SH", "招商银行"),
                ("600519.SH", "贵州茅台"),
                ("000858.SZ", "五粮液"),
                ("000002.SZ", "万科A"),
                ("600000.SH", "浦发银行")
            ]
            
            cols = st.columns(3)
            for i, (symbol, name) in enumerate(popular_stocks):
                with cols[i % 3]:
                    if st.button(f"📊 {name}", key=f"{key}_popular_{i}", use_container_width=True):
                        new_selection = f"{symbol} - {name}"
                        st.session_state[session_key] = new_selection
                        st.success(f"✅ 已选择: **{name}** ({symbol})")
                        st.rerun()
        
        if search_input.strip():
            # 实时搜索建议
            search_results = stock_mapper.search_stocks(search_input.strip(), limit=10)
            
            if search_results:
                st.markdown(f"**🎯 找到 {len(search_results)} 个匹配结果:**")
                
                # 使用列布局显示搜索结果
                num_cols = min(2, len(search_results))
                cols = st.columns(num_cols)
                
                for i, result in enumerate(search_results):
                    col_idx = i % num_cols
                    with cols[col_idx]:
                        result_key = f"{key}_result_{result['symbol']}"
                        
                        # 显示匹配类型信息
                        match_info = ""
                        if 'match_type' in result:
                            match_types = {
                                'exact_code': '🎯 精确代码',
                                'code': '📝 代码匹配', 
                                'exact_name': '🎯 精确名称',
                                'name': '📝 名称匹配',
                                'fuzzy': '🔍 模糊匹配'
                            }
                            match_info = match_types.get(result['match_type'], '🔍 匹配')
                        
                        button_text = f"📊 {result['name']}\n`{result['symbol']}` {match_info}"
                        
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
                st.info("💡 **搜索建议**:")
                st.markdown("- 📝 输入股票代码: `000001`, `600519.SH`")
                st.markdown("- 📝 输入股票名称: `平安银行`, `贵州茅台`") 
                st.markdown("- 📝 输入常用简称: `中行`, `工行`, `茅台`")
                st.markdown("- 🔍 支持部分匹配: `银行`, `白酒`, `科技`")
    
    else:
        # 方式2: 下拉选择框（移到第二选项）
        with st.container():
            selected_stock = st.selectbox(
                "从完整列表中选择股票",
                options=stock_options,
                index=current_index,
                key=f"{key}_main_select",
                help="📋 浏览完整股票列表，支持键盘输入快速定位"
            )
            
            # 更新session state
            if selected_stock != st.session_state[session_key]:
                st.session_state[session_key] = selected_stock
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
