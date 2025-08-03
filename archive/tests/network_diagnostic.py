#!/usr/bin/env python3
"""
网络连接诊断脚本
"""

import sys
import os
import requests
import socket
import subprocess
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_system_info():
    """检查系统信息"""
    print("🔍 系统信息检查")
    print("=" * 40)
    
    try:
        # Python版本
        print(f"Python版本: {sys.version}")
        
        # 网络接口
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"主机名: {hostname}")
        print(f"本地IP: {local_ip}")
        
        # DNS配置
        print("\nDNS配置:")
        try:
            with open('/etc/resolv.conf', 'r') as f:
                dns_info = f.read()
                print(dns_info.strip()[:200])
        except Exception as e:
            print(f"无法读取DNS配置: {e}")
        
    except Exception as e:
        print(f"系统信息检查失败: {e}")

def check_network_connectivity():
    """检查网络连接"""
    print("\n🌐 网络连接检查")
    print("=" * 40)
    
    test_hosts = [
        ("百度", "https://www.baidu.com"),
        ("谷歌", "https://www.google.com"),
        ("GitHub", "https://github.com"),
        ("本地Streamlit", "http://localhost:8501"),
        ("本地IP", "http://127.0.0.1:8501")
    ]
    
    for name, url in test_hosts:
        try:
            response = requests.get(url, timeout=5)
            status = "✅" if response.status_code == 200 else f"⚠️ ({response.status_code})"
            print(f"{status} {name}: {url}")
        except requests.exceptions.Timeout:
            print(f"⏰ {name}: 超时")
        except requests.exceptions.ConnectionError:
            print(f"❌ {name}: 连接失败")
        except Exception as e:
            print(f"❌ {name}: {e}")

def check_firewall():
    """检查防火墙状态"""
    print("\n🔥 防火墙检查")
    print("=" * 40)
    
    try:
        # 检查ufw状态
        result = subprocess.run(['ufw', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("UFW状态:")
            print(result.stdout)
        else:
            print("UFW未安装或无法访问")
    except FileNotFoundError:
        print("UFW未安装")
    except Exception as e:
        print(f"防火墙检查失败: {e}")
    
    try:
        # 检查iptables
        result = subprocess.run(['iptables', '-L'], capture_output=True, text=True)
        if result.returncode == 0:
            print("\niptables规则:")
            lines = result.stdout.split('\n')[:10]  # 只显示前10行
            print('\n'.join(lines))
        else:
            print("无法访问iptables")
    except FileNotFoundError:
        print("iptables未安装")
    except Exception as e:
        print(f"iptables检查失败: {e}")

def check_streamlit_status():
    """检查Streamlit状态"""
    print("\n📱 Streamlit状态检查")
    print("=" * 40)
    
    try:
        # 检查进程
        result = subprocess.run(['pgrep', '-f', 'streamlit'], capture_output=True, text=True)
        if result.stdout:
            pids = result.stdout.strip().split('\n')
            print(f"Streamlit进程: {', '.join(pids)}")
            
            # 检查端口占用
            result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if ':8501' in line:
                    print(f"端口8501状态: {line.strip()}")
        else:
            print("未发现Streamlit进程")
    except Exception as e:
        print(f"Streamlit状态检查失败: {e}")

def check_browser_requirements():
    """检查浏览器要求"""
    print("\n🌍 浏览器要求检查")
    print("=" * 40)
    
    print("Streamlit建议的浏览器:")
    print("✅ Chrome (推荐)")
    print("✅ Firefox")
    print("✅ Safari")
    print("✅ Edge")
    print()
    print("如果遇到网络错误，可能的解决方案:")
    print("1. 禁用浏览器广告拦截器")
    print("2. 清除浏览器缓存和Cookie")
    print("3. 尝试无痕/隐私模式")
    print("4. 检查是否有企业防火墙阻止")
    print("5. 尝试使用不同的浏览器")

def generate_fix_suggestions():
    """生成修复建议"""
    print("\n🛠️ 修复建议")
    print("=" * 40)
    
    print("针对 'net::ERR_CONNECTION_RESET' 错误的解决方案:")
    print()
    print("1. 浏览器层面:")
    print("   - 清除缓存: Ctrl+Shift+Delete")
    print("   - 禁用扩展程序")
    print("   - 重启浏览器")
    print()
    print("2. 网络层面:")
    print("   - 检查防火墙设置")
    print("   - 重启网络连接")
    print("   - 尝试使用VPN或代理")
    print()
    print("3. 应用层面:")
    print("   - 重启Streamlit应用")
    print("   - 使用不同的端口")
    print("   - 检查应用日志")
    print()
    print("4. 系统层面:")
    print("   - 检查系统时间")
    print("   - 更新系统包")
    print("   - 重启系统")

def main():
    """主函数"""
    print("🔧 网络连接诊断工具")
    print(f"诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 执行各项检查
    check_system_info()
    check_network_connectivity()
    check_firewall()
    check_streamlit_status()
    check_browser_requirements()
    generate_fix_suggestions()
    
    print("\n" + "=" * 60)
    print("📋 诊断完成")
    print("如果问题仍然存在，请查看上述建议并尝试相应的解决方案。")

if __name__ == "__main__":
    main()
