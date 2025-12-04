"""
Flask Web应用主文件

提供穿搭分析的Web接口，包括图片上传、分析、推荐等功能。
"""

import os
import sys
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import json
from datetime import datetime
from typing import Dict, Any, Optional

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.core import (
    extract_dominant_colors,
    classify_color_type,
    evaluate_color_combo,
    RuleEvaluator,
    StyleRecognizer,
    create_evaluator
)

# Flask应用配置
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'static/templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB最大文件大小
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static/images/uploads')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

# CORS 配置（允许 Cloudflare Pages 前端调用）
from flask_cors import CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],  # 生产环境应该指定具体域名
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 全局对象（延迟加载）
style_recognizer: Optional[StyleRecognizer] = None
rule_evaluator: Optional[RuleEvaluator] = None


def init_models(model_path: Optional[str] = None):
    """
    初始化模型（延迟加载）

    参数:
        model_path: 可选的模型路径；如果未提供，则使用 app.config['MODEL_PATH'] 或默认路径
    """
    global style_recognizer, rule_evaluator

    # 确定模型路径优先级：参数 > 配置 > 默认路径
    if model_path is None:
        model_path = app.config.get(
            'MODEL_PATH',
            os.path.join(BASE_DIR, 'models/best_model.h5')
        )

    if style_recognizer is None:
        if model_path and os.path.exists(model_path):
            try:
                print(f"加载款式识别模型: {model_path}")
                style_recognizer = StyleRecognizer(model_path)
            except Exception as e:
                print(f"警告: 无法加载款式识别模型: {e}")
                style_recognizer = None
        else:
            print(f"提示: 未找到款式识别模型文件: {model_path}，将仅使用颜色和规则分析")

    if rule_evaluator is None:
        rule_evaluator = create_evaluator()


def allowed_file(filename: str) -> bool:
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def save_uploaded_file(file) -> Optional[str]:
    """保存上传的文件"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # 添加时间戳避免文件名冲突
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filepath
    return None


@app.route('/')
def index():
    """主页：上传页面"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    """接收图片上传"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '没有上传文件'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '文件名为空'
            }), 400
        
        # 保存文件
        filepath = save_uploaded_file(file)
        if not filepath:
            return jsonify({
                'success': False,
                'error': '不支持的文件格式，请上传图片文件（png, jpg, jpeg, gif, bmp）'
            }), 400
        
        # 返回文件信息（使用相对路径）
        relative_path = os.path.relpath(filepath, BASE_DIR)
        return jsonify({
            'success': True,
            'filepath': relative_path,
            'filename': os.path.basename(filepath),
            'url': f"/images/uploads/{os.path.basename(filepath)}"
        })
    
    except RequestEntityTooLarge:
        return jsonify({
            'success': False,
            'error': '文件太大，最大支持16MB'
        }), 413
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'上传失败: {str(e)}'
        }), 500


@app.route('/analyze', methods=['POST'])
def analyze():
    """分析穿搭"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据格式错误'
            }), 400
        
        filepath = data.get('filepath')
        if not filepath:
            return jsonify({
                'success': False,
                'error': '缺少文件路径'
            }), 400
        
        # 转换为绝对路径
        if not os.path.isabs(filepath):
            filepath = os.path.join(BASE_DIR, filepath)
        
        # 检查文件是否存在
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': '文件不存在'
            }), 404
        
        # 初始化模型
        init_models()
        
        # 1. 提取主色调
        try:
            colors_data = extract_dominant_colors(filepath, n_colors=5)
            colors = [color for color, _ in colors_data]
            colors_with_percent = []
            
            for color, percentage in colors_data:
                # 确保color是Python原生int类型的元组
                color_tuple = tuple(int(c) for c in color)
                
                color_info = classify_color_type(color_tuple)
                colors_with_percent.append({
                    'rgb': list(color_tuple),
                    'percentage': round(float(percentage), 2),
                    'name': color_info['name'],
                    'tone': color_info['tone']
                })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': f'颜色提取失败: {str(e)}'
            }), 500
        
        # 2. 识别款式（优先使用用户提供的款式，其次使用模型识别）
        styles = data.get('styles', {}) or {}  # 获取用户提供的款式
        style_predictions = []
        
        # 如果用户没有提供款式，尝试使用模型识别
        if not styles and style_recognizer:
            try:
                predictions = style_recognizer.predict(filepath, top_k=3)
                style_predictions = predictions
                if predictions:
                    styles = {
                        'top': predictions[0]['class'] if 'top' in filepath.lower() else None,
                        'bottom': predictions[0]['class'] if 'bottom' in filepath.lower() else None,
                        'shoes': predictions[0]['class'] if 'shoes' in filepath.lower() else None,
                    }
            except Exception as e:
                print(f"款式识别失败: {e}")
        
        # 3. 颜色搭配评估
        color_evaluation = evaluate_color_combo(colors)
        
        # 4. 规则评估
        context = data.get('context', {})
        rule_result = None
        if rule_evaluator:
            try:
                # 确保colors是正确的格式
                colors_for_eval = [tuple(c) if isinstance(c, (list, tuple)) else c for c in colors]
                rule_result = rule_evaluator.evaluate_outfit(
                    colors=colors_for_eval,
                    styles=styles if styles else None,
                    context=context if context else None
                )
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"规则评估失败: {e}")
        
        # 构建返回结果
        result = {
            'success': True,
            'image_url': f"/images/uploads/{os.path.basename(filepath)}",
            'colors': colors_with_percent,
            'color_evaluation': {
                'score': color_evaluation['score'],
                'suggestions': color_evaluation['suggestions']
            },
            'style_predictions': style_predictions,
            'rule_evaluation': rule_result,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'分析失败: {str(e)}'
        }), 500


@app.route('/recommend', methods=['GET'])
def recommend():
    """基于场景的推荐"""
    try:
        context_type = request.args.get('context', '休闲')
        
        # 初始化评估器
        init_models()
        
        # 根据场景类型提供推荐
        context_recommendations = {
            '正式场合': {
                'colors': ['黑', '白', '灰', '深蓝', '深灰'],
                'styles': {'top': '衬衫', 'bottom': '休闲裤', 'shoes': '皮鞋'},
                'tips': [
                    '选择经典的黑白灰配色',
                    '正装风格，避免过于花哨',
                    '皮鞋是正式场合的最佳选择',
                    '保持整体简洁大气'
                ]
            },
            '商务': {
                'colors': ['深蓝', '深灰', '白', '黑'],
                'styles': {'top': '衬衫', 'bottom': '休闲裤', 'shoes': '皮鞋'},
                'tips': [
                    '商务场合以稳重为主',
                    '深色系更显专业',
                    '保持整洁干净的形象',
                    '避免过于鲜艳的颜色'
                ]
            },
            '工作': {
                'colors': ['白', '蓝', '灰', '黑'],
                'styles': {'top': '衬衫', 'bottom': '休闲裤', 'shoes': '皮鞋'},
                'tips': [
                    '工作场合要专业但不失活力',
                    '可以选择一些亮色作为点缀',
                    '舒适度也很重要',
                    '选择透气性好的面料'
                ]
            },
            '休闲': {
                'colors': ['白', '蓝', '灰', '黑', '棕'],
                'styles': {'top': 'T恤', 'bottom': '牛仔裤', 'shoes': '运动鞋'},
                'tips': [
                    '休闲场合可以更自由',
                    '选择舒适的单品',
                    '颜色可以更丰富',
                    '搭配要协调即可'
                ]
            },
            '运动': {
                'colors': ['黑', '白', '灰', '蓝', '红'],
                'styles': {'top': 'T恤', 'bottom': '休闲裤', 'shoes': '运动鞋'},
                'tips': [
                    '运动场合以舒适为主',
                    '选择透气性好的材质',
                    '颜色可以更鲜艳',
                    '运动鞋是必备单品'
                ]
            }
        }
        
        # 获取对应场景的推荐，如果不存在则使用休闲作为默认
        rec = context_recommendations.get(context_type, context_recommendations['休闲'])
        
        return jsonify({
            'success': True,
            'context': context_type,
            'recommendations': rec.get('tips', []),
            'color_suggestions': rec.get('colors', []),
            'style_suggestions': rec.get('styles', {})
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取推荐失败: {str(e)}'
        }), 500


@app.route('/wardrobe', methods=['GET'])
def wardrobe():
    """虚拟衣柜管理"""
    try:
        # 获取上传目录中的所有图片
        upload_dir = app.config['UPLOAD_FOLDER']
        images = []
        
        if os.path.exists(upload_dir):
            for filename in os.listdir(upload_dir):
                if allowed_file(filename):
                    filepath = os.path.join(upload_dir, filename)
                    file_stat = os.stat(filepath)
                    images.append({
                        'filename': filename,
                        'url': f"/images/uploads/{filename}",
                        'uploaded_at': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                        'size': file_stat.st_size
                    })
        
        # 按上传时间排序
        images.sort(key=lambda x: x['uploaded_at'], reverse=True)
        
        return jsonify({
            'success': True,
            'images': images,
            'count': len(images)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取衣柜失败: {str(e)}'
        }), 500


@app.route('/images/uploads/<filename>')
def uploaded_file(filename):
    """提供上传的图片文件"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        'success': False,
        'error': '页面不存在'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({
        'success': False,
        'error': '服务器内部错误'
    }), 500


if __name__ == '__main__':
    # 直接运行此模块时，使用默认配置启动（主要用于开发调试）
    init_models()
    app.run(debug=True, host='0.0.0.0', port=5000)

