#!/usr/bin/env python3
"""简化风险分析调试脚本"""

import sys
sys.path.append('.')

print("开始风险分析调试...")

try:
    from src.ai.risk_manager import RiskManager
    print("✅ 成功导入 RiskManager")
    
    from src.data.data_fetcher import DataFetcher
    print("✅ 成功导入 DataFetcher")
    
    # 创建实例
    risk_manager = RiskManager()
    data_fetcher = DataFetcher()
    print("✅ 成功创建实例")
    
    # 测试单只股票
    stock_code = "600036.SH"
    print(f"\n🧪 测试股票: {stock_code}")
    
    # 获取数据
    data = data_fetcher.get_stock_data(stock_code, period='6m')
    if data is None or data.empty:
        print("❌ 数据获取失败")
        sys.exit(1)
    
    print(f"✅ 数据获取成功，数据长度: {len(data)}")
    print(f"📊 数据列名: {data.columns.tolist()}")
    
    # 测试风险评估
    print("\n🔍 开始风险评估...")
    risk_result = risk_manager.assess_risk(data)  # 只传递数据，不传递股票代码
    
    if isinstance(risk_result, dict) and 'overall_risk' in risk_result:
        overall_risk = risk_result['overall_risk']
        risk_score = overall_risk.get('score', 0)
        risk_level = overall_risk.get('level', '未知')
        
        print(f"💰 风险得分: {risk_score:.2f}")
        print(f"🏷️ 风险等级: {risk_level}")
        
        # 测试阈值
        print(f"\n🎯 风险等级阈值分析:")
        print(f"得分 {risk_score:.2f}:")
        if risk_score >= 75:
            print(f"✅ >= 75 → 极低风险")
        elif risk_score >= 60:
            print(f"✅ >= 60 → 低风险") 
        elif risk_score >= 40:
            print(f"✅ >= 40 → 中等风险")
        elif risk_score >= 25:
            print(f"✅ >= 25 → 高风险")
        else:
            print(f"✅ < 25 → 极高风险")
    else:
        print(f"❌ 风险评估结果异常: {risk_result}")
    
    print("\n✅ 测试完成")

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
