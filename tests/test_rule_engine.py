"""
规则引擎单元测试
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.rule_engine import (
    RuleEvaluator,
    ThreeColorRule,
    LightTopDarkBottomRule,
    ForbiddenColorComboRule,
    StyleCoordinationRule,
    ContextAppropriateRule,
    RuleLibrary,
    RuleSeverity
)


def test_three_color_rule():
    """测试三色原则"""
    print("=" * 60)
    print("测试1: 三色原则")
    print("=" * 60)
    
    rule = ThreeColorRule(max_colors=3)
    
    # 测试符合规则
    result1 = rule.evaluate({
        'colors': [(255, 0, 0), (0, 0, 255), (255, 255, 255)]  # 红、蓝、白（白是中性色）
    })
    print(f"测试1-1: 3种颜色（含中性色）")
    print(f"  结果: {'通过' if result1.passed else '失败'}, 评分: {result1.score:.1f}")
    print(f"  信息: {result1.message}")
    assert result1.passed, "应该通过三色原则"
    
    # 测试违反规则
    result2 = rule.evaluate({
        'colors': [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]  # 4种主色
    })
    print(f"\n测试1-2: 4种主色")
    print(f"  结果: {'通过' if result2.passed else '失败'}, 评分: {result2.score:.1f}")
    print(f"  信息: {result2.message}")
    assert not result2.passed, "应该违反三色原则"
    
    print("✓ 三色原则测试通过\n")


def test_forbidden_color_combo():
    """测试禁忌颜色组合"""
    print("=" * 60)
    print("测试2: 禁忌颜色组合")
    print("=" * 60)
    
    rule = ForbiddenColorComboRule()
    
    # 测试红绿组合
    result1 = rule.evaluate({
        'colors': [(255, 0, 0), (0, 255, 0)]  # 红、绿
    })
    print(f"测试2-1: 红绿组合")
    print(f"  结果: {'通过' if result1.passed else '失败'}, 评分: {result1.score:.1f}")
    print(f"  信息: {result1.message}")
    assert not result1.passed, "应该检测到红绿禁忌组合"
    
    # 测试正常组合
    result2 = rule.evaluate({
        'colors': [(255, 0, 0), (0, 0, 255)]  # 红、蓝
    })
    print(f"\n测试2-2: 红蓝组合")
    print(f"  结果: {'通过' if result2.passed else '失败'}, 评分: {result2.score:.1f}")
    print(f"  信息: {result2.message}")
    assert result2.passed, "红蓝组合应该通过"
    
    print("✓ 禁忌颜色组合测试通过\n")


def test_style_coordination():
    """测试款式协调"""
    print("=" * 60)
    print("测试3: 款式协调")
    print("=" * 60)
    
    rule = StyleCoordinationRule()
    
    # 测试正装协调
    result1 = rule.evaluate({
        'styles': {'top': '衬衫', 'bottom': '休闲裤', 'shoes': '皮鞋'}
    })
    print(f"测试3-1: 衬衫+休闲裤+皮鞋")
    print(f"  结果: {'通过' if result1.passed else '失败'}, 评分: {result1.score:.1f}")
    print(f"  信息: {result1.message}")
    
    # 测试休闲装协调
    result2 = rule.evaluate({
        'styles': {'top': 'T恤', 'bottom': '牛仔裤', 'shoes': '运动鞋'}
    })
    print(f"\n测试3-2: T恤+牛仔裤+运动鞋")
    print(f"  结果: {'通过' if result2.passed else '失败'}, 评分: {result2.score:.1f}")
    print(f"  信息: {result2.message}")
    assert result2.passed, "休闲装应该协调"
    
    print("✓ 款式协调测试通过\n")


def test_context_appropriate():
    """测试场景适宜"""
    print("=" * 60)
    print("测试4: 场景适宜")
    print("=" * 60)
    
    rule = ContextAppropriateRule()
    
    # 测试正式场合
    result1 = rule.evaluate({
        'context': {'type': '正式场合'},
        'styles': {'top': 'T恤', 'bottom': '牛仔裤', 'shoes': '运动鞋'}
    })
    print(f"测试4-1: 正式场合穿休闲装")
    print(f"  结果: {'通过' if result1.passed else '失败'}, 评分: {result1.score:.1f}")
    print(f"  信息: {result1.message}")
    assert not result1.passed, "正式场合不应该穿休闲装"
    
    # 测试休闲场合
    result2 = rule.evaluate({
        'context': {'type': '休闲'},
        'styles': {'top': 'T恤', 'bottom': '牛仔裤', 'shoes': '运动鞋'}
    })
    print(f"\n测试4-2: 休闲场合穿休闲装")
    print(f"  结果: {'通过' if result2.passed else '失败'}, 评分: {result2.score:.1f}")
    print(f"  信息: {result2.message}")
    assert result2.passed, "休闲场合应该穿休闲装"
    
    print("✓ 场景适宜测试通过\n")


def test_rule_evaluator():
    """测试规则评估器"""
    print("=" * 60)
    print("测试5: 规则评估器")
    print("=" * 60)
    
    evaluator = RuleEvaluator()
    
    # 测试完整评估
    result = evaluator.evaluate_outfit(
        colors=[(255, 0, 0), (0, 255, 0)],  # 红绿（禁忌）
        styles={'top': 'T恤', 'bottom': '牛仔裤', 'shoes': '运动鞋'},
        context={'type': '休闲'}
    )
    
    print(f"总体评分: {result['score']}")
    print(f"是否通过: {result['passed']}")
    print(f"通过规则: {result['summary']['passed_rules']}/{result['summary']['total_rules']}")
    print(f"错误数: {result['summary']['errors']}, 警告数: {result['summary']['warnings']}")
    
    assert 'score' in result
    assert 'passed' in result
    assert 'results' in result
    assert 'suggestions' in result
    assert 'summary' in result
    
    print("✓ 规则评估器测试通过\n")


def test_rule_library():
    """测试规则库"""
    print("=" * 60)
    print("测试6: 规则库")
    print("=" * 60)
    
    library = RuleLibrary()
    
    print(f"默认规则数: {len(library.rules)}")
    print("规则列表:")
    for rule in library.rules:
        print(f"  - {rule.name}: {rule.description} (权重: {rule.weight})")
    
    # 测试禁用规则
    library.disable_rule('三色原则')
    enabled_rules = library.get_enabled_rules()
    print(f"\n禁用'三色原则'后，启用规则数: {len(enabled_rules)}")
    
    # 测试启用规则
    library.enable_rule('三色原则')
    enabled_rules = library.get_enabled_rules()
    print(f"重新启用'三色原则'后，启用规则数: {len(enabled_rules)}")
    
    assert len(enabled_rules) == len(library.rules)
    
    print("✓ 规则库测试通过\n")


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("规则引擎单元测试")
    print("=" * 60 + "\n")
    
    try:
        test_three_color_rule()
        test_forbidden_color_combo()
        test_style_coordination()
        test_context_appropriate()
        test_rule_evaluator()
        test_rule_library()
        
        print("=" * 60)
        print("所有测试通过！")
        print("=" * 60)
        return True
    except AssertionError as e:
        print(f"\n测试失败: {e}")
        return False
    except Exception as e:
        print(f"\n测试出错: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    main()

