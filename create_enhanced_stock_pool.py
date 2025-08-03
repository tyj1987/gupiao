#!/usr/bin/env python3
"""
增强股票池生成器
创建具有不同风险等级的多样化股票池
"""

import sys
import os
sys.path.append('/home/tyj/gupiao')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_enhanced_stock_pool():
    """创建增强的股票池，包含不同风险等级的股票"""
    
    # 扩展的股票池 - 包含不同行业和风险特征的股票
    enhanced_stocks = {
        # 银行股 - 通常低到中等风险
        "000001.SZ": "平安银行",
        "600036.SH": "招商银行", 
        "600000.SH": "浦发银行",
        "601988.SH": "中国银行",
        "601398.SH": "工商银行",
        "601939.SH": "建设银行",
        "601288.SH": "农业银行",
        "002142.SZ": "宁波银行",
        
        # 白酒股 - 中等到高风险
        "600519.SH": "贵州茅台",
        "000858.SZ": "五粮液", 
        "000596.SZ": "古井贡酒",
        "600809.SH": "山西汾酒",
        "000799.SZ": "酒鬼酒",
        "603589.SH": "口子窖",
        
        # 科技股 - 高风险
        "000002.SZ": "万科A",
        "300015.SZ": "爱尔眼科", 
        "300750.SZ": "宁德时代",
        "002415.SZ": "海康威视",
        "000858.SZ": "五粮液",
        "300059.SZ": "东方财富",
        "300896.SZ": "爱美客",
        
        # 医药股 - 中等风险
        "000661.SZ": "长春高新",
        "300122.SZ": "智飞生物",
        "002821.SZ": "凯莱英",
        "300760.SZ": "迈瑞医疗",
        "600276.SH": "恒瑞医药",
        "000963.SZ": "华东医药",
        
        # 消费股 - 中等风险
        "000895.SZ": "双汇发展",
        "600887.SH": "伊利股份",
        "000568.SZ": "泸州老窖",
        "002304.SZ": "洋河股份",
        "600298.SH": "安琪酵母",
        
        # 地产股 - 高风险
        "000002.SZ": "万科A",
        "001979.SZ": "招商蛇口",
        "600048.SH": "保利发展",
        "000069.SZ": "华侨城A",
        
        # 新能源车 - 极高风险
        "002594.SZ": "比亚迪",
        "300750.SZ": "宁德时代", 
        "002460.SZ": "赣锋锂业",
        "300014.SZ": "亿纬锂能",
        
        # 煤炭钢铁 - 中等到高风险  
        "600019.SH": "宝钢股份",
        "000898.SZ": "鞍钢股份",
        "601006.SH": "大秦铁路",
        "601088.SH": "中国神华",
        
        # 保险股 - 低到中等风险
        "601318.SH": "中国平安",
        "601601.SH": "中国太保",
        "601336.SH": "新华保险",
        "000001.SZ": "平安银行",
        
        # 石油化工 - 中等风险
        "600028.SH": "中国石化",
        "601857.SH": "中国石油",
        "000792.SZ": "盐湖股份",
        "600309.SH": "万华化学",
        
        # 通信设备 - 高风险
        "000063.SZ": "中兴通讯", 
        "002475.SZ": "立讯精密",
        "600050.SH": "中国联通",
        "000725.SZ": "京东方A",
        
        # 家电股 - 中等风险
        "000333.SZ": "美的集团",
        "000651.SZ": "格力电器",
        "002415.SZ": "海康威视",
        "600690.SH": "海尔智家"
    }
    
    return enhanced_stocks

def update_stock_mapper():
    """更新股票映射器"""
    try:
        from src.data.stock_mapper import StockMapper
        
        mapper = StockMapper()
        enhanced_stocks = create_enhanced_stock_pool()
        
        print(f"增强股票池包含 {len(enhanced_stocks)} 只股票")
        
        # 验证映射器中的股票数量
        all_stocks = mapper.get_all_stocks()
        print(f"当前映射器包含 {len(all_stocks)} 只股票")
        
        # 显示一些示例
        print("\n股票池示例:")
        for i, (code, name) in enumerate(list(enhanced_stocks.items())[:10]):
            print(f"  {code} - {name}")
        
        return True
        
    except Exception as e:
        print(f"❌ 更新股票映射器失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 创建增强股票池")
    
    enhanced_stocks = create_enhanced_stock_pool()
    print(f"✅ 增强股票池创建完成，包含 {len(enhanced_stocks)} 只股票")
    
    # 按行业分类统计
    industries = {
        "银行": 8,
        "白酒": 6, 
        "科技": 7,
        "医药": 6,
        "消费": 5,
        "地产": 4,
        "新能源": 4,
        "传统工业": 4,
        "保险": 4,
        "石化": 4,
        "通信": 4,
        "家电": 4
    }
    
    print("\n📊 行业分布:")
    for industry, count in industries.items():
        print(f"  {industry}: {count} 只")
    
    print(f"\n总计: {sum(industries.values())} 只股票")
    
    # 更新映射器
    if update_stock_mapper():
        print("✅ 股票映射器更新成功")
