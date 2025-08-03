"""
股票AI分析助手 - 简化Web界面
专为新手股民设计的智能投资工具
"""

import streamlit as st
import datetime
import random
import time

# 页面配置
st.set_page_config(
    page_title="股票AI分析助手",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 模拟数据
def get_mock_stock_data():
    """获取模拟股票数据"""
    stocks = [
        {"code": "600519.SH", "name": "贵州茅台", "price": 1680.00, "change": -0.8, "score": 85},
        {"code": "000001.SZ", "name": "平安银行", "price": 12.34, "change": 1.2, "score": 82},
        {"code": "600036.SH", "name": "招商银行", "price": 35.20, "change": 0.5, "score": 80},
        {"code": "000002.SZ", "name": "万科A", "price": 15.67, "change": -1.1, "score": 78},
        {"code": "600000.SH", "name": "浦发银行", "price": 8.45, "change": 0.8, "score": 75},
    ]
    return stocks

def get_mock_analysis(stock_code):
    """获取模拟分析数据"""
    return {
        "score": random.randint(60, 95),
        "recommendation": random.choice(["买入", "持有", "卖出"]),
        "target_price": random.uniform(10, 200),
        "risk_level": random.choice(["低", "中", "高"]),
        "technical_indicators": {
            "MA5": random.uniform(10, 100),
            "MA20": random.uniform(10, 100),
            "RSI": random.uniform(20, 80),
            "MACD": random.uniform(-2, 2),
        }
    }

# 主界面
def main():
    st.title("📈 股票AI分析助手")
    st.markdown("**专为新手股民设计的智能投资工具**")
    st.warning("⚠️ 这是简化演示版本，使用模拟数据")

    # 侧边栏
    st.sidebar.title("🔧 功能菜单")
    page = st.sidebar.selectbox(
        "选择功能",
        ["📊 股票分析", "🎯 智能选股", "⚡ 自动交易", "🛡️ 风险管理", "📚 投资学堂"]
    )

    if page == "📊 股票分析":
        show_stock_analysis()
    elif page == "🎯 智能选股":
        show_stock_screening()
    elif page == "⚡ 自动交易":
        show_auto_trading()
    elif page == "🛡️ 风险管理":
        show_risk_management()
    elif page == "📚 投资学堂":
        show_education()

def show_stock_analysis():
    """股票分析页面"""
    st.header("📊 股票分析")
    
    # 股票代码输入
    col1, col2 = st.columns([2, 1])
    with col1:
        stock_code = st.text_input("请输入股票代码", value="600519.SH", placeholder="例如: 600519.SH")
    with col2:
        if st.button("🔍 分析", type="primary"):
            with st.spinner("正在分析中..."):
                time.sleep(1)
                st.success("分析完成！")

    if stock_code:
        # 模拟分析结果
        analysis = get_mock_analysis(stock_code)
        
        # 显示基本信息
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("AI评分", f"{analysis['score']}分", "2.1")
        with col2:
            st.metric("投资建议", analysis['recommendation'])
        with col3:
            st.metric("目标价格", f"¥{analysis['target_price']:.2f}")
        with col4:
            st.metric("风险等级", analysis['risk_level'])

        # 技术指标
        st.subheader("📈 技术指标")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**移动平均线**")
            st.write(f"MA5: {analysis['technical_indicators']['MA5']:.2f}")
            st.write(f"MA20: {analysis['technical_indicators']['MA20']:.2f}")
        
        with col2:
            st.write("**动量指标**")
            st.write(f"RSI: {analysis['technical_indicators']['RSI']:.2f}")
            st.write(f"MACD: {analysis['technical_indicators']['MACD']:.2f}")

        # 投资建议
        st.subheader("💡 投资建议")
        if analysis['score'] >= 80:
            st.success("🟢 强烈推荐：技术指标良好，建议买入")
        elif analysis['score'] >= 70:
            st.info("🔵 一般推荐：可适量买入或持有")
        else:
            st.warning("🟡 谨慎操作：建议观望或减仓")

def show_stock_screening():
    """智能选股页面"""
    st.header("🎯 智能选股")
    
    # 筛选条件
    st.subheader("🔍 筛选条件")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_score = st.slider("最低AI评分", 60, 100, 75)
    with col2:
        max_price = st.slider("最高价格(元)", 1, 1000, 100)
    with col3:
        industry = st.selectbox("行业", ["全部", "金融", "科技", "医药", "消费"])

    if st.button("🔍 开始筛选", type="primary"):
        with st.spinner("正在筛选中..."):
            time.sleep(1)
            
            # 显示筛选结果
            stocks = get_mock_stock_data()
            filtered_stocks = [s for s in stocks if s['score'] >= min_score and s['price'] <= max_price]
            
            st.subheader(f"📋 筛选结果 (共{len(filtered_stocks)}只)")
            
            if filtered_stocks:
                for i, stock in enumerate(filtered_stocks, 1):
                    col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 1, 1])
                    with col1:
                        st.write(f"**{i}**")
                    with col2:
                        st.write(f"**{stock['code']}**")
                    with col3:
                        st.write(stock['name'])
                    with col4:
                        st.write(f"¥{stock['price']}")
                    with col5:
                        if stock['score'] >= 80:
                            st.success(f"{stock['score']}分")
                        else:
                            st.info(f"{stock['score']}分")
            else:
                st.info("暂无符合条件的股票")

def show_auto_trading():
    """自动交易页面"""
    st.header("⚡ 自动交易")
    
    # 交易策略选择
    st.subheader("🎯 交易策略")
    strategy = st.selectbox(
        "选择策略",
        ["保守策略", "平衡策略", "激进策略"]
    )
    
    # 策略说明
    if strategy == "保守策略":
        st.info("🛡️ 保守策略：低风险，稳健收益，适合新手")
    elif strategy == "平衡策略":
        st.info("⚖️ 平衡策略：中等风险，平衡收益，适合有经验投资者")
    else:
        st.info("🚀 激进策略：高风险高收益，适合风险承受能力强的投资者")

    # 交易参数
    st.subheader("⚙️ 交易参数")
    col1, col2 = st.columns(2)
    
    with col1:
        max_position = st.slider("最大仓位(%)", 10, 100, 80)
        stop_loss = st.slider("止损点(%)", 1, 20, 10)
    
    with col2:
        take_profit = st.slider("止盈点(%)", 5, 50, 20)
        max_stocks = st.slider("最多持股数", 1, 20, 5)

    # 模拟交易状态
    st.subheader("📊 交易状态")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("总资产", "¥108,500", "2.1%")
    with col2:
        st.metric("今日收益", "¥1,200", "1.1%")
    with col3:
        st.metric("持仓股票", "3只")
    with col4:
        st.metric("可用资金", "¥25,000")

    # 启动/停止按钮
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 启动自动交易", type="primary"):
            st.success("✅ 自动交易已启动")
    with col2:
        if st.button("⏹️ 停止交易"):
            st.warning("⏸️ 自动交易已停止")

def show_risk_management():
    """风险管理页面"""
    st.header("🛡️ 风险管理")
    
    # 投资组合概览
    st.subheader("📊 投资组合概览")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("总资产", "¥108,500")
        st.metric("股票资产", "¥83,500 (77%)")
    with col2:
        st.metric("现金资产", "¥25,000 (23%)")
        st.metric("今日收益", "¥1,200 (+1.1%)")
    with col3:
        st.metric("持仓股票", "3只")
        st.metric("风险评级", "中等")

    # 风险评估
    st.subheader("⚠️ 风险评估")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**风险指标**")
        st.success("🟢 流动性风险: 低")
        st.warning("🟡 集中度风险: 中")
        st.success("🟢 市场风险: 低")
        st.warning("🟡 行业风险: 中")
    
    with col2:
        st.write("**改进建议**")
        st.write("• 适当增加其他行业股票")
        st.write("• 保持20%以上现金比例")
        st.write("• 单只股票仓位不超过30%")
        st.write("• 定期重新平衡投资组合")

    # 风险预警
    st.subheader("🚨 风险预警")
    st.info("暂无风险预警")

def show_education():
    """投资学堂页面"""
    st.header("📚 投资学堂")
    
    # 学习模块
    st.subheader("📖 学习模块")
    
    with st.expander("1. 股票投资基础"):
        st.write("""
        **什么是股票？**
        股票是股份公司发行的所有权凭证，代表持股人对公司的部分所有权。
        
        **如何开户？**
        1. 选择证券公司
        2. 准备身份证和银行卡
        3. 填写开户申请
        4. 风险评估和签署协议
        
        **交易规则**
        • 交易时间：周一至周五 9:30-11:30, 13:00-15:00
        • 涨跌幅限制：普通股票±10%，ST股票±5%
        • 最小交易单位：100股（1手）
        """)
    
    with st.expander("2. 风险管理"):
        st.write("""
        **分散投资原则**
        不要把所有资金投入同一只股票，建议分散投资5-10只不同行业的股票。
        
        **止损止盈策略**
        • 止损：当亏损达到预设比例时及时卖出
        • 止盈：当盈利达到目标时适时获利了结
        
        **仓位管理**
        • 新手建议股票仓位不超过总资产的50%
        • 单只股票仓位不超过总资产的20%
        • 保持一定现金比例以应对机会和风险
        """)
    
    with st.expander("3. 技术分析"):
        st.write("""
        **常用技术指标**
        • MA（移动平均线）：反映价格趋势
        • RSI（相对强弱指标）：判断超买超卖
        • MACD：趋势和动量指标
        • KDJ：短期买卖信号
        
        **K线图基础**
        • 红色（阳线）：收盘价高于开盘价
        • 绿色（阴线）：收盘价低于开盘价
        • 上影线：最高价与收盘价的差
        • 下影线：最低价与开盘价的差
        """)

    # 投资格言
    st.subheader("💡 投资格言")
    quotes = [
        "投资有风险，入市需谨慎",
        "不要把鸡蛋放在一个篮子里",
        "时间是最好的朋友",
        "买入优质公司并长期持有",
        "市场总是在恐惧和贪婪中摆动"
    ]
    
    for quote in quotes:
        st.info(f"💭 {quote}")

# 运行应用
if __name__ == "__main__":
    main()
