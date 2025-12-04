"""
Flask应用启动脚本

方便启动Web应用的入口文件。
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.web.app import app

if __name__ == '__main__':
    print("=" * 60)
    print("穿搭分析系统 - Outfit Simulator")
    print("=" * 60)
    print("正在启动Web应用...")
    print("访问地址: http://localhost:5000")
    print("按 Ctrl+C 停止服务")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

