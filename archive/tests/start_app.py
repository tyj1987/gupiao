#!/usr/bin/env python3
"""
应用启动脚本 - 确保系统稳定运行
"""

import os
import sys
import time
import subprocess
import logging

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app_startup.log')
    ]
)

logger = logging.getLogger(__name__)

def check_dependencies():
    """检查依赖项"""
    logger.info("检查系统依赖...")
    
    try:
        import streamlit
        import pandas
        import numpy
        import sklearn
        import plotly
        logger.info("✅ 核心依赖检查通过")
        return True
    except ImportError as e:
        logger.error(f"❌ 依赖缺失: {e}")
        return False

def clean_models():
    """清理机器学习模型"""
    logger.info("清理机器学习模型...")
    
    models_dir = 'models'
    if os.path.exists(models_dir):
        import shutil
        shutil.rmtree(models_dir)
        logger.info("✅ 已清理旧模型")
    
    # 确保模型目录存在
    os.makedirs(models_dir, exist_ok=True)
    logger.info("✅ 模型目录准备完成")

def prepare_environment():
    """准备运行环境"""
    logger.info("准备运行环境...")
    
    # 设置环境变量
    os.environ['PYTHONPATH'] = os.getcwd()
    os.environ['STREAMLIT_SERVER_PORT'] = '8501'
    os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    
    # 禁用一些可能导致网络请求的功能
    os.environ['STREAMLIT_BROWSER_SERVER_ADDRESS'] = 'localhost'
    os.environ['STREAMLIT_GLOBAL_DEV_MODE'] = 'false'
    
    logger.info("✅ 环境变量配置完成")

def test_basic_functionality():
    """测试基础功能"""
    logger.info("测试基础功能...")
    
    try:
        # 测试数据获取
        from src.data.data_fetcher import DataFetcher
        fetcher = DataFetcher()
        logger.info("✅ 数据获取器初始化成功")
        
        # 测试数据处理
        from src.data.data_processor import DataProcessor
        processor = DataProcessor()
        logger.info("✅ 数据处理器初始化成功")
        
        # 测试AI分析
        from src.ai.stock_analyzer import StockAnalyzer
        analyzer = StockAnalyzer()
        logger.info("✅ 股票分析器初始化成功")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 功能测试失败: {e}")
        return False

def start_streamlit():
    """启动Streamlit应用"""
    logger.info("启动Streamlit应用...")
    
    try:
        # 构建启动命令
        cmd = [
            sys.executable, '-m', 'streamlit', 'run',
            'src/ui/streamlit_app.py',
            '--server.port', '8501',
            '--server.address', '0.0.0.0',
            '--server.headless', 'true',
            '--browser.gatherUsageStats', 'false',
            '--browser.serverAddress', 'localhost',
            '--global.developmentMode', 'false'
        ]
        
        logger.info(f"执行命令: {' '.join(cmd)}")
        
        # 启动应用
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        logger.info("Streamlit应用已启动")
        logger.info("访问地址: http://localhost:8501")
        
        # 等待应用启动
        time.sleep(3)
        
        # 检查进程状态
        if process.poll() is None:
            logger.info("✅ 应用运行正常")
            return True
        else:
            stdout, stderr = process.communicate()
            logger.error(f"❌ 应用启动失败")
            logger.error(f"STDOUT: {stdout}")
            logger.error(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 启动失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 股票分析系统启动中...")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        logger.error("❌ 依赖检查失败，请先安装必要的依赖")
        return False
    
    # 清理模型
    clean_models()
    
    # 准备环境
    prepare_environment()
    
    # 测试功能
    if not test_basic_functionality():
        logger.error("❌ 功能测试失败")
        return False
    
    # 启动应用
    if not start_streamlit():
        logger.error("❌ 应用启动失败")
        return False
    
    print("=" * 50)
    print("🎉 系统启动成功！")
    print("📱 访问地址: http://localhost:8501")
    print("📖 使用说明:")
    print("   1. 在浏览器中打开上述地址")
    print("   2. 输入股票代码进行分析")
    print("   3. 支持中国股票(如: 000001.SZ)和美股(如: AAPL)")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("用户中断程序")
    except Exception as e:
        logger.error(f"程序异常: {e}")
