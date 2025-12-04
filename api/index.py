"""
Vercel 部署入口文件

这个文件是 Vercel 的入口点，导入并运行 Flask 应用。
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入 Flask 应用
from src.web.app import app

# Vercel 需要这个变量
# 注意：变量名必须是 'app'
app = app

# 如果直接运行此文件（本地测试）
if __name__ == '__main__':
    app.run(debug=True)
