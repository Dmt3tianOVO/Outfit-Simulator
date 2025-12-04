"""
颜色分析模块的单元测试

测试颜色分类和颜色搭配评估功能（不需要图像文件）
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.color_analyzer import (
    classify_color_type,
    evaluate_color_combo,
    calculate_color_distance
)


def test_classify_color_type():
    """测试颜色分类功能"""
    print("=" * 60)
    print("测试1: 颜色分类功能")
    print("=" * 60)
    
    test_cases = [
        ((255, 0, 0), '红', '暖色'),
        ((0, 255, 0), '绿', '冷色'),
        ((0, 0, 255), '蓝', '冷色'),
        ((255, 255, 0), '黄', '暖色'),
        ((0, 0, 0), '黑', '中性'),
        ((255, 255, 255), '白', '中性'),
        ((128, 128, 128), '灰', '中性'),
        ((255, 165, 0), '橙', '暖色'),
        ((128, 0, 128), '紫', '冷色'),
        ((139, 69, 19), '棕', '暖色'),
    ]
    
    passed = 0
    failed = 0
    
    for rgb, expected_name, expected_tone in test_cases:
        result = classify_color_type(rgb)
        name_match = expected_name in result['name'] or result['name'] in expected_name
        tone_match = result['tone'] == expected_tone
        
        rgb_str = str(rgb)
        if name_match and tone_match:
            print(f"✓ RGB{rgb_str:20} -> {result['name']:6} ({result['tone']})")
            passed += 1
        else:
            print(f"✗ RGB{rgb_str:20} -> {result['name']:6} ({result['tone']}) [期望: {expected_name} ({expected_tone})]")
            failed += 1
    
    print(f"\n通过: {passed}, 失败: {failed}")
    return failed == 0


def test_evaluate_color_combo():
    """测试颜色搭配评估功能"""
    print("\n" + "=" * 60)
    print("测试2: 颜色搭配评估功能")
    print("=" * 60)
    
    test_cases = [
        {
            'name': '三色协调搭配（红绿蓝）',
            'colors': [(255, 0, 0), (0, 255, 0), (0, 0, 255)],
            'min_score': 50,
        },
        {
            'name': '暖色系搭配',
            'colors': [(255, 100, 50), (255, 200, 0), (200, 150, 100)],
            'min_score': 60,
        },
        {
            'name': '中性色+彩色（黑白红）',
            'colors': [(0, 0, 0), (255, 255, 255), (255, 0, 0)],
            'min_score': 70,
        },
        {
            'name': '相似颜色（低对比度）',
            'colors': [(100, 100, 100), (110, 110, 110), (120, 120, 120)],
            'min_score': 40,
        },
        {
            'name': '单色搭配',
            'colors': [(100, 150, 200)],
            'min_score': 100,
        },
        {
            'name': '过多颜色',
            'colors': [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)],
            'min_score': 30,
        },
    ]
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        result = evaluate_color_combo(test_case['colors'])
        score = result['score']
        min_score = test_case['min_score']
        
        print(f"\n{test_case['name']}:")
        print(f"  颜色: {test_case['colors']}")
        print(f"  评分: {score} (最低期望: {min_score})")
        print(f"  建议:")
        for suggestion in result['suggestions'][:3]:  # 只显示前3条建议
            print(f"    - {suggestion}")
        
        if score >= min_score:
            print(f"  ✓ 通过")
            passed += 1
        else:
            print(f"  ✗ 失败 (评分低于期望)")
            failed += 1
    
    print(f"\n通过: {passed}, 失败: {failed}")
    return failed == 0


def test_calculate_color_distance():
    """测试颜色距离计算"""
    print("\n" + "=" * 60)
    print("测试3: 颜色距离计算")
    print("=" * 60)
    
    test_cases = [
        (((0, 0, 0), (255, 255, 255)), 441.67),  # 黑白对比度最高
        (((255, 0, 0), (0, 255, 0)), 360.62),    # 红绿对比
        (((100, 100, 100), (110, 110, 110)), 17.32),  # 相似颜色
    ]
    
    passed = 0
    failed = 0
    
    for (color1, color2), expected_min in test_cases:
        distance = calculate_color_distance(color1, color2)
        print(f"RGB{color1} <-> RGB{color2}: {distance:.2f} (期望 >= {expected_min})")
        
        if distance >= expected_min * 0.9:  # 允许10%误差
            print(f"  ✓ 通过")
            passed += 1
        else:
            print(f"  ✗ 失败")
            failed += 1
    
    print(f"\n通过: {passed}, 失败: {failed}")
    return failed == 0


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("颜色分析模块单元测试")
    print("=" * 60)
    
    results = []
    results.append(("颜色分类", test_classify_color_type()))
    results.append(("颜色搭配评估", test_evaluate_color_combo()))
    results.append(("颜色距离计算", test_calculate_color_distance()))
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{name:20} {status}")
    
    all_passed = all(result[1] for result in results)
    print("=" * 60)
    if all_passed:
        print("所有测试通过！")
    else:
        print("部分测试失败，请检查代码。")
    print("=" * 60)
    
    return all_passed


if __name__ == '__main__':
    main()


