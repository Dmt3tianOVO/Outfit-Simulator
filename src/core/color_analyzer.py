"""
颜色分析模块

提供图像颜色提取、颜色分类和颜色搭配评估功能。
使用OpenCV进行图像处理，使用scikit-learn进行K-means聚类。
"""
import cv2
import numpy as np
from sklearn.cluster import KMeans
from typing import List, Tuple, Dict
import math


def extract_dominant_colors(image_path: str, n_colors: int = 3) -> List[Tuple[Tuple[int, int, int], float]]:
    """
    使用K-means聚类提取图像的主色调
    
    参数:
        image_path (str): 图像文件路径
        n_colors (int): 要提取的主色调数量，默认为3
    
    返回:
        List[Tuple[Tuple[int, int, int], float]]: 
            颜色列表，每个元素为((R, G, B), 占比百分比)
            按占比从高到低排序
    
    示例:
        >>> colors = extract_dominant_colors('image.jpg', n_colors=3)
        >>> print(colors)
        [((120, 45, 200), 45.2), ((200, 180, 150), 30.5), ((50, 50, 50), 24.3)]
    """
    # 读取图像
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"无法读取图像文件: {image_path}")
    
    # 将BGR转换为RGB（OpenCV默认使用BGR格式）
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # 将图像重塑为像素列表 (height * width, 3)
    pixels = image.reshape(-1, 3)
    
    # 使用K-means聚类提取主色调
    # n_init=10: 运行10次不同的初始化，选择最佳结果
    # random_state=42: 设置随机种子以确保结果可复现
    kmeans = KMeans(n_clusters=n_colors, n_init=10, random_state=42)
    kmeans.fit(pixels)
    
    # 获取聚类中心（主色调RGB值）
    colors = kmeans.cluster_centers_.astype(int)
    
    # 计算每个颜色的占比
    labels = kmeans.labels_
    total_pixels = len(labels)
    color_counts = {}
    
    for i, label in enumerate(labels):
        # 转换为Python原生int类型，避免numpy类型问题
        color_tuple = tuple(int(c) for c in colors[label])
        color_counts[color_tuple] = color_counts.get(color_tuple, 0) + 1
    
    # 计算占比并排序
    color_percentages = []
    for color, count in color_counts.items():
        percentage = (count / total_pixels) * 100
        color_percentages.append((color, percentage))
    
    # 按占比从高到低排序
    color_percentages.sort(key=lambda x: x[1], reverse=True)
    
    return color_percentages


def classify_color_type(rgb: Tuple[int, int, int]) -> Dict[str, str]:
    """
    将RGB颜色值归类为颜色类型和色系
    
    参数:
        rgb (Tuple[int, int, int]): RGB颜色值，范围0-255
    
    返回:
        Dict[str, str]: 包含以下键的字典
            - 'name': 颜色名称（如'红'、'蓝'、'黑'等）
            - 'tone': 色系（'冷色'、'暖色'、'中性'）
    
    颜色分类规则:
        - 黑白灰: 基于亮度判断
        - 彩色: 基于RGB值的相对大小判断主色调
        - 色系: 红/橙/黄为暖色，蓝/绿/紫为冷色，黑白灰为中性
    
    示例:
        >>> result = classify_color_type((255, 0, 0))
        >>> print(result)
        {'name': '红', 'tone': '暖色'}
    """
    # 转换为Python原生int类型，处理numpy类型
    r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
    
    # 计算亮度（使用标准亮度公式）
    brightness = 0.299 * r + 0.587 * g + 0.114 * b
    
    # 计算RGB的最大值和最小值
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    diff = max_val - min_val
    
    # 判断是否为黑白灰
    if diff < 30:  # RGB值接近，可能是黑白灰
        if brightness < 30:
            return {'name': '黑', 'tone': '中性'}
        elif brightness > 225:
            return {'name': '白', 'tone': '中性'}
        else:
            return {'name': '灰', 'tone': '中性'}
    
    # 判断主色调
    # 计算各颜色的相对强度
    total = r + g + b
    if total == 0:
        return {'name': '黑', 'tone': '中性'}
    
    r_ratio = r / total
    g_ratio = g / total
    b_ratio = b / total
    
    # 棕色系（低亮度的橙红色，需要优先判断）
    if brightness < 150 and r > 50 and g > 30 and b < min(r, g) * 0.7 and r > b and g > b:
        return {'name': '棕', 'tone': '暖色'}
    
    # 黄色/橙色系（需要优先于红色判断）
    if r_ratio > 0.35 and g_ratio > 0.3 and r > b and g > b:
        # 橙色：红色明显大于绿色，且绿色也较大
        if r > g * 1.15 and g > 100:
            return {'name': '橙', 'tone': '暖色'}
        else:
            # 黄色
            if brightness > 200:
                return {'name': '浅黄', 'tone': '暖色'}
            else:
                return {'name': '黄', 'tone': '暖色'}
    
    # 红色系
    if r_ratio > 0.4 and r > g and r > b:
        if brightness > 200:
            return {'name': '粉', 'tone': '暖色'}
        elif brightness < 80:
            return {'name': '深红', 'tone': '暖色'}
        else:
            return {'name': '红', 'tone': '暖色'}
    
    # 绿色系
    if g_ratio > 0.35 and g > r and g > b:
        if brightness > 200:
            return {'name': '浅绿', 'tone': '冷色'}
        elif brightness < 100:
            return {'name': '深绿', 'tone': '冷色'}
        else:
            return {'name': '绿', 'tone': '冷色'}
    
    # 蓝色系
    if b_ratio > 0.4 and b > r and b > g:
        if brightness > 200:
            return {'name': '浅蓝', 'tone': '冷色'}
        elif brightness < 100:
            return {'name': '深蓝', 'tone': '冷色'}
        else:
            return {'name': '蓝', 'tone': '冷色'}
    
    # 紫色系
    if r_ratio > 0.3 and b_ratio > 0.3 and r > g and b > g:
        if brightness > 200:
            return {'name': '浅紫', 'tone': '冷色'}
        elif brightness < 100:
            return {'name': '深紫', 'tone': '冷色'}
        else:
            return {'name': '紫', 'tone': '冷色'}
    
    # 默认情况：根据主要颜色判断
    if max_val == r:
        return {'name': '红', 'tone': '暖色'}
    elif max_val == g:
        return {'name': '绿', 'tone': '冷色'}
    else:
        return {'name': '蓝', 'tone': '冷色'}


def calculate_color_distance(color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float:
    """
    计算两个颜色之间的欧氏距离（用于评估颜色对比度）
    
    参数:
        color1: RGB颜色值1
        color2: RGB颜色值2
    
    返回:
        float: 颜色距离（0-441.67，值越大对比度越高）
    """
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)


def evaluate_color_combo(colors_list: List[Tuple[int, int, int]]) -> Dict[str, any]:
    """
    评估颜色搭配是否协调
    
    基于以下规则进行评估:
    1. 三色原则：主色调不超过3种
    2. 对比度：颜色之间需要有适当对比度
    3. 色系协调：冷色、暖色、中性色的搭配
    4. 避免冲突色：互补色需要谨慎搭配
    
    参数:
        colors_list (List[Tuple[int, int, int]]): RGB颜色列表
    
    返回:
        Dict[str, any]: 包含以下键的字典
            - 'score': 评分(0-100)
            - 'suggestions': 改进建议列表
            - 'analysis': 详细分析信息
    
    示例:
        >>> colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        >>> result = evaluate_color_combo(colors)
        >>> print(result['score'])
        65
    """
    if not colors_list:
        return {
            'score': 0,
            'suggestions': ['请提供至少一种颜色'],
            'analysis': {}
        }
    
    if len(colors_list) == 1:
        return {
            'score': 100,
            'suggestions': ['单色搭配，简洁优雅'],
            'analysis': {'color_count': 1}
        }
    
    score = 100
    suggestions = []
    analysis = {
        'color_count': len(colors_list),
        'color_types': [],
        'tones': [],
        'contrast_scores': []
    }
    
    # 1. 三色原则检查
    if len(colors_list) > 3:
        score -= 20
        suggestions.append('建议主色调不超过3种，当前有{}种颜色'.format(len(colors_list)))
    elif len(colors_list) == 3:
        suggestions.append('符合三色原则，搭配协调')
    
    # 2. 颜色分类和色系分析
    color_types = []
    tones = []
    for color in colors_list:
        color_info = classify_color_type(color)
        color_types.append(color_info['name'])
        tones.append(color_info['tone'])
    
    analysis['color_types'] = color_types
    analysis['tones'] = tones
    
    # 统计色系分布
    warm_count = tones.count('暖色')
    cold_count = tones.count('冷色')
    neutral_count = tones.count('中性')
    
    # 3. 色系协调性检查
    if warm_count > 0 and cold_count > 0:
        # 冷暖色搭配需要中性色过渡
        if neutral_count == 0:
            score -= 15
            suggestions.append('冷暖色搭配时，建议加入中性色（黑/白/灰）作为过渡')
        else:
            suggestions.append('冷暖色搭配良好，中性色起到了很好的过渡作用')
    
    # 4. 对比度检查
    min_contrast = float('inf')
    max_contrast = 0
    
    for i in range(len(colors_list)):
        for j in range(i + 1, len(colors_list)):
            contrast = calculate_color_distance(colors_list[i], colors_list[j])
            analysis['contrast_scores'].append(contrast)
            min_contrast = min(min_contrast, contrast)
            max_contrast = max(max_contrast, contrast)
    
    # 对比度过低（颜色太相似）
    if min_contrast < 50:
        score -= 20
        suggestions.append('部分颜色过于相似，缺乏层次感，建议增加对比度')
    elif min_contrast < 100:
        score -= 10
        suggestions.append('部分颜色对比度较低，可考虑增加一些对比')
    
    # 对比度过高（可能过于刺眼）
    if max_contrast > 400:
        score -= 10
        suggestions.append('部分颜色对比度过高，可能显得刺眼，建议适当降低对比度')
    
    # 5. 冲突色检查（互补色需要谨慎）
    # 红-绿、蓝-橙、黄-紫是互补色
    complementary_pairs = [
        (('红', '深红', '粉'), ('绿', '深绿', '浅绿')),
        (('蓝', '深蓝', '浅蓝'), ('橙', '黄', '浅黄')),
        (('黄', '浅黄'), ('紫', '深紫', '浅紫'))
    ]
    
    has_complementary = False
    for pair1, pair2 in complementary_pairs:
        if any(c in pair1 for c in color_types) and any(c in pair2 for c in color_types):
            has_complementary = True
            break
    
    if has_complementary and neutral_count == 0:
        score -= 15
        suggestions.append('检测到互补色搭配，建议加入中性色（黑/白/灰）来平衡')
    elif has_complementary:
        suggestions.append('互补色搭配得当，中性色起到了很好的平衡作用')
    
    # 6. 黑白灰的合理使用
    if neutral_count == len(colors_list):
        suggestions.append('中性色搭配，经典且安全')
    elif neutral_count > 0 and neutral_count < len(colors_list):
        suggestions.append('中性色与彩色搭配，平衡且优雅')
    
    # 确保分数在0-100范围内
    score = max(0, min(100, score))
    
    # 如果没有问题，添加正面评价
    if score >= 80 and not suggestions:
        suggestions.append('颜色搭配协调，评分优秀')
    
    return {
        'score': round(score, 1),
        'suggestions': suggestions,
        'analysis': analysis
    }


# ==================== 单元测试示例 ====================

if __name__ == '__main__':
    print("=" * 60)
    print("颜色分析模块单元测试")
    print("=" * 60)
    
    # 测试1: 颜色分类
    print("\n【测试1】颜色分类测试")
    print("-" * 60)
    test_colors = [
        (255, 0, 0),      # 红色
        (0, 255, 0),      # 绿色
        (0, 0, 255),      # 蓝色
        (255, 255, 0),    # 黄色
        (0, 0, 0),        # 黑色
        (255, 255, 255),  # 白色
        (128, 128, 128),  # 灰色
        (255, 165, 0),    # 橙色
        (128, 0, 128),    # 紫色
        (139, 69, 19),    # 棕色
    ]
    
    for rgb in test_colors:
        result = classify_color_type(rgb)
        rgb_str = str(rgb)
        print(f"RGB{rgb_str:20} -> {result['name']:6} ({result['tone']})")
    
    # 测试2: 颜色搭配评估
    print("\n【测试2】颜色搭配评估测试")
    print("-" * 60)
    
    # 测试用例1: 三色协调搭配
    combo1 = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]  # 红绿蓝
    result1 = evaluate_color_combo(combo1)
    print(f"\n搭配1: RGB{combo1}")
    print(f"评分: {result1['score']}")
    print("建议:")
    for suggestion in result1['suggestions']:
        print(f"  - {suggestion}")
    
    # 测试用例2: 暖色系搭配
    combo2 = [(255, 100, 50), (255, 200, 0), (200, 150, 100)]  # 橙、黄、棕
    result2 = evaluate_color_combo(combo2)
    print(f"\n搭配2: RGB{combo2}")
    print(f"评分: {result2['score']}")
    print("建议:")
    for suggestion in result2['suggestions']:
        print(f"  - {suggestion}")
    
    # 测试用例3: 中性色+彩色搭配
    combo3 = [(0, 0, 0), (255, 255, 255), (255, 0, 0)]  # 黑、白、红
    result3 = evaluate_color_combo(combo3)
    print(f"\n搭配3: RGB{combo3}")
    print(f"评分: {result3['score']}")
    print("建议:")
    for suggestion in result3['suggestions']:
        print(f"  - {suggestion}")
    
    # 测试用例4: 相似颜色（低对比度）
    combo4 = [(100, 100, 100), (110, 110, 110), (120, 120, 120)]  # 相似灰色
    result4 = evaluate_color_combo(combo4)
    print(f"\n搭配4: RGB{combo4}")
    print(f"评分: {result4['score']}")
    print("建议:")
    for suggestion in result4['suggestions']:
        print(f"  - {suggestion}")
    
    # 测试用例5: 单色
    combo5 = [(100, 150, 200)]
    result5 = evaluate_color_combo(combo5)
    print(f"\n搭配5: RGB{combo5}")
    print(f"评分: {result5['score']}")
    print("建议:")
    for suggestion in result5['suggestions']:
        print(f"  - {suggestion}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    
    # 注意：extract_dominant_colors 需要实际的图像文件才能测试
    # 可以在有图像文件时取消下面的注释进行测试
    """
    print("\n【测试3】主色调提取测试（需要图像文件）")
    print("-" * 60)
    try:
        # 替换为实际的图像路径
        image_path = 'static/images/test.jpg'
        colors = extract_dominant_colors(image_path, n_colors=3)
        print(f"\n图像: {image_path}")
        print("提取的主色调:")
        for i, (color, percentage) in enumerate(colors, 1):
            color_info = classify_color_type(color)
            print(f"  {i}. RGB{color:15} 占比: {percentage:.2f}%  -> {color_info['name']} ({color_info['tone']})")
    except Exception as e:
        print(f"测试失败: {e}")
        print("提示: 请确保有可用的测试图像文件")
    """

