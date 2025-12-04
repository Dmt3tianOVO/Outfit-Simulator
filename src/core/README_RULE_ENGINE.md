# 穿搭规则引擎使用说明

## 概述

穿搭规则引擎提供基于规则的穿搭评估功能，包括颜色、款式和场景规则。规则可配置，易于扩展。

## 功能特点

- **模块化设计**：规则分为颜色规则、款式规则、场景规则三大类
- **可配置**：每个规则可以设置权重和启用/禁用状态
- **易于扩展**：可以轻松添加自定义规则
- **详细反馈**：提供评分、建议和严重程度信息

## 规则列表

### 颜色规则

1. **三色原则** (`ThreeColorRule`)
   - 全身主色调不超过3种
   - 权重：1.5

2. **上浅下深原则** (`LightTopDarkBottomRule`)
   - 上衣颜色应该比下装颜色浅
   - 权重：1.2

3. **禁忌颜色组合** (`ForbiddenColorComboRule`)
   - 避免互补色直接搭配（红绿、紫黄、蓝橙）
   - 权重：1.8

### 款式规则

4. **款式协调** (`StyleCoordinationRule`)
   - 上下装和鞋子的风格应该协调
   - 正装配正装，休闲装配休闲装
   - 权重：1.5

### 场景规则

5. **场景适宜** (`ContextAppropriateRule`)
   - 根据场景选择合适的穿搭风格
   - 支持场景：正式场合、商务、工作、休闲、运动、聚会
   - 权重：1.3

## 使用方法

### 基本使用

```python
from src.core.rule_engine import evaluate_outfit

# 评估穿搭
result = evaluate_outfit(
    colors=[(255, 0, 0), (0, 0, 255), (255, 255, 255)],  # RGB颜色
    styles={'top': '衬衫', 'bottom': '休闲裤', 'shoes': '皮鞋'},
    context={'type': '工作'}
)

print(f"评分: {result['score']}")
print(f"是否通过: {result['passed']}")
print(f"建议数: {len(result['suggestions'])}")
```

### 使用评估器类

```python
from src.core.rule_engine import RuleEvaluator

# 创建评估器
evaluator = RuleEvaluator()

# 评估穿搭
result = evaluator.evaluate_outfit(
    colors=[(255, 0, 0), (0, 255, 0)],  # 红、绿（禁忌组合）
    styles={'top': 'T恤', 'bottom': '牛仔裤', 'shoes': '运动鞋'},
    context={'type': '休闲'},
    top_colors=[(255, 0, 0)],      # 上衣颜色
    bottom_colors=[(0, 255, 0)]     # 下装颜色
)

# 查看结果
print(f"总体评分: {result['score']}")
print(f"通过规则: {result['summary']['passed_rules']}/{result['summary']['total_rules']}")
print(f"错误数: {result['summary']['errors']}, 警告数: {result['summary']['warnings']}")

# 查看各规则评估结果
for rule_result in result['results']:
    status = "✓" if rule_result['passed'] else "✗"
    print(f"{status} {rule_result['rule_name']}: {rule_result['message']}")

# 查看改进建议
for suggestion in result['suggestions']:
    print(f"[{suggestion['severity']}] {suggestion['suggestion']}")
```

### 配置规则

```python
from src.core.rule_engine import RuleEvaluator

evaluator = RuleEvaluator()

# 禁用某个规则
evaluator.rule_library.disable_rule('三色原则')

# 修改规则权重
evaluator.configure_rule('禁忌颜色组合', weight=2.0)

# 重新启用规则
evaluator.rule_library.enable_rule('三色原则')
```

### 添加自定义规则

```python
from src.core.rule_engine import ColorRule, RuleResult, RuleSeverity

class CustomColorRule(ColorRule):
    """自定义颜色规则示例"""
    
    def __init__(self):
        super().__init__(
            name="自定义规则",
            description="示例自定义规则",
            weight=1.0
        )
    
    def _evaluate_colors(self, colors, outfit_data):
        # 实现评估逻辑
        if len(colors) > 5:
            return RuleResult(
                passed=False,
                score=50.0,
                message="颜色过多",
                suggestion="建议减少颜色数量",
                severity=RuleSeverity.WARNING,
                weight=self.weight
            )
        else:
            return RuleResult(
                passed=True,
                score=100.0,
                message="颜色数量合适",
                weight=self.weight
            )

# 添加自定义规则
evaluator = RuleEvaluator()
custom_rule = CustomColorRule()
evaluator.add_custom_rule(custom_rule)
```

## 输入格式

### colors（颜色列表）

可以是以下格式之一：
- RGB元组：`[(255, 0, 0), (0, 255, 0)]` - 会自动分类
- 颜色名称：`['红', '蓝', '白']` - 直接使用

### styles（款式字典）

```python
{
    'top': '衬衫',      # 上衣：T恤、衬衫、卫衣、外套
    'bottom': '牛仔裤',  # 下装：牛仔裤、休闲裤
    'shoes': '皮鞋'     # 鞋子：运动鞋、皮鞋
}
```

### context（场景字典）

```python
{
    'type': '工作'  # 场景类型：正式场合、商务、工作、休闲、运动、聚会
}
```

## 输出格式

```python
{
    'score': 85.5,           # 总体评分（0-100）
    'passed': True,           # 是否通过（无严重错误）
    'results': [              # 各规则评估结果
        {
            'rule_name': '三色原则',
            'rule_description': '全身主色调不超过3种',
            'passed': True,
            'score': 100.0,
            'message': '符合三色原则，主色调有2种',
            'suggestion': None,
            'severity': 'info',
            'weight': 1.5
        },
        # ... 更多规则结果
    ],
    'suggestions': [          # 改进建议
        {
            'rule': '款式协调',
            'suggestion': '建议统一风格以获得更好的视觉效果',
            'severity': 'warning'
        }
    ],
    'summary': {              # 评估摘要
        'total_rules': 5,
        'passed_rules': 4,
        'failed_rules': 1,
        'errors': 0,
        'warnings': 1
    }
}
```

## 规则严重程度

- **INFO**: 信息提示，不影响评分
- **WARNING**: 警告，轻微违反规则
- **ERROR**: 错误，严重违反规则，会导致`passed=False`

## 完整示例

```python
from src.core.rule_engine import RuleEvaluator
from src.core.color_analyzer import extract_dominant_colors, classify_color_type

# 创建评估器
evaluator = RuleEvaluator()

# 从图像提取颜色
colors_data = extract_dominant_colors('outfit.jpg', n_colors=3)
colors = [color for color, _ in colors_data]

# 评估穿搭
result = evaluator.evaluate_outfit(
    colors=colors,
    styles={'top': '衬衫', 'bottom': '牛仔裤', 'shoes': '皮鞋'},
    context={'type': '工作'}
)

# 显示结果
print("=" * 60)
print("穿搭评估结果")
print("=" * 60)
print(f"总体评分: {result['score']}/100")
print(f"状态: {'通过' if result['passed'] else '未通过'}")
print(f"\n规则评估:")
for r in result['results']:
    status = "✓" if r['passed'] else "✗"
    print(f"  {status} {r['rule_name']:15} - {r['message']}")

if result['suggestions']:
    print(f"\n改进建议:")
    for s in result['suggestions']:
        print(f"  - [{s['severity']}] {s['suggestion']}")
```

## 注意事项

1. **颜色格式**：如果提供RGB元组，会自动调用颜色分类函数；如果提供颜色名称字符串，直接使用
2. **中性色**：黑、白、灰不计入三色原则的主色调
3. **规则权重**：权重影响总体评分，权重越大，该规则对总分的影响越大
4. **扩展性**：可以通过继承`BaseRule`、`ColorRule`、`StyleRule`或`ContextRule`创建自定义规则

