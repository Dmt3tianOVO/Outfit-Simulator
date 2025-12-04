"""
穿搭规则引擎模块

提供基于规则的穿搭评估功能，包括颜色、款式和场景规则。
规则可配置，易于扩展。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


# 导入颜色分析功能
try:
    from .color_analyzer import classify_color_type
except ImportError:
    from color_analyzer import classify_color_type


class RuleSeverity(Enum):
    """规则严重程度"""
    INFO = "info"          # 信息提示
    WARNING = "warning"    # 警告
    ERROR = "error"        # 错误（严重违反）


@dataclass
class RuleResult:
    """规则评估结果"""
    passed: bool                    # 是否通过
    score: float                    # 评分（0-100）
    message: str                    # 规则说明
    suggestion: Optional[str] = None  # 改进建议
    severity: RuleSeverity = RuleSeverity.INFO  # 严重程度
    weight: float = 1.0            # 规则权重


class BaseRule(ABC):
    """规则基类"""
    
    def __init__(self, name: str, description: str, weight: float = 1.0, enabled: bool = True):
        """
        初始化规则
        
        参数:
            name: 规则名称
            description: 规则描述
            weight: 规则权重（用于计算总分）
            enabled: 是否启用该规则
        """
        self.name = name
        self.description = description
        self.weight = weight
        self.enabled = enabled
    
    @abstractmethod
    def evaluate(self, outfit_data: Dict[str, Any]) -> RuleResult:
        """
        评估规则
        
        参数:
            outfit_data: 穿搭数据字典，包含colors、styles、context等信息
        
        返回:
            RuleResult: 规则评估结果
        """
        pass
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}', enabled={self.enabled})"


class ColorRule(BaseRule):
    """颜色相关规则基类"""
    
    def evaluate(self, outfit_data: Dict[str, Any]) -> RuleResult:
        """评估颜色规则"""
        colors = outfit_data.get('colors', [])
        if not colors:
            return RuleResult(
                passed=True,
                score=100.0,
                message="未提供颜色信息，跳过颜色规则检查",
                severity=RuleSeverity.INFO
            )
        return self._evaluate_colors(colors, outfit_data)
    
    @abstractmethod
    def _evaluate_colors(self, colors: List[Any], outfit_data: Dict[str, Any]) -> RuleResult:
        """评估颜色（子类实现）"""
        pass


class StyleRule(BaseRule):
    """款式相关规则基类"""
    
    def evaluate(self, outfit_data: Dict[str, Any]) -> RuleResult:
        """评估款式规则"""
        styles = outfit_data.get('styles', {})
        if not styles:
            return RuleResult(
                passed=True,
                score=100.0,
                message="未提供款式信息，跳过款式规则检查",
                severity=RuleSeverity.INFO
            )
        return self._evaluate_styles(styles, outfit_data)
    
    @abstractmethod
    def _evaluate_styles(self, styles: Dict[str, str], outfit_data: Dict[str, Any]) -> RuleResult:
        """评估款式（子类实现）"""
        pass


class ContextRule(BaseRule):
    """场景相关规则基类"""
    
    def evaluate(self, outfit_data: Dict[str, Any]) -> RuleResult:
        """评估场景规则"""
        context = outfit_data.get('context', {})
        if not context:
            return RuleResult(
                passed=True,
                score=100.0,
                message="未提供场景信息，跳过场景规则检查",
                severity=RuleSeverity.INFO
            )
        return self._evaluate_context(context, outfit_data)
    
    @abstractmethod
    def _evaluate_context(self, context: Dict[str, Any], outfit_data: Dict[str, Any]) -> RuleResult:
        """评估场景（子类实现）"""
        pass


# ==================== 具体规则实现 ====================

class ThreeColorRule(ColorRule):
    """三色原则：全身不超过三个主色"""
    
    def __init__(self, max_colors: int = 3, weight: float = 1.5):
        super().__init__(
            name="三色原则",
            description=f"全身主色调不超过{max_colors}种",
            weight=weight
        )
        self.max_colors = max_colors
    
    def _evaluate_colors(self, colors: List[Any], outfit_data: Dict[str, Any]) -> RuleResult:
        """
        评估三色原则
        
        参数:
            colors: 颜色列表，每个元素可以是RGB元组或颜色名称字符串
        """
        # 提取主色调（排除黑白灰等中性色）
        main_colors = []
        neutral_colors = {'黑', '白', '灰'}
        
        for color in colors:
            if isinstance(color, tuple):
                # RGB值，需要分类
                color_info = classify_color_type(color)
                color_name = color_info['name']
            else:
                color_name = str(color)
            
            if color_name not in neutral_colors:
                if color_name not in main_colors:
                    main_colors.append(color_name)
        
        num_main_colors = len(main_colors)
        
        if num_main_colors <= self.max_colors:
            score = 100.0
            passed = True
            message = f"符合三色原则，主色调有{num_main_colors}种"
            suggestion = None
            severity = RuleSeverity.INFO
        else:
            score = max(0, 100 - (num_main_colors - self.max_colors) * 20)
            passed = False
            message = f"违反三色原则，主色调有{num_main_colors}种（建议不超过{self.max_colors}种）"
            suggestion = f"建议减少主色调数量，保留{self.max_colors}种主要颜色，其他使用中性色（黑/白/灰）"
            severity = RuleSeverity.WARNING
        
        return RuleResult(
            passed=passed,
            score=score,
            message=message,
            suggestion=suggestion,
            severity=severity,
            weight=self.weight
        )


class LightTopDarkBottomRule(ColorRule):
    """上浅下深原则：上衣颜色比下装浅"""
    
    def __init__(self, weight: float = 1.2):
        super().__init__(
            name="上浅下深原则",
            description="上衣颜色应该比下装颜色浅",
            weight=weight
        )
    
    def _evaluate_colors(self, colors: List[Any], outfit_data: Dict[str, Any]) -> RuleResult:
        """评估上浅下深原则"""
        top_colors = outfit_data.get('top_colors', [])
        bottom_colors = outfit_data.get('bottom_colors', [])
        
        if not top_colors or not bottom_colors:
            return RuleResult(
                passed=True,
                score=100.0,
                message="未提供上下装颜色信息，跳过检查",
                severity=RuleSeverity.INFO,
                weight=self.weight
            )
        
        # 计算平均亮度
        def get_brightness(color):
            if isinstance(color, tuple):
                r, g, b = color
                return 0.299 * r + 0.587 * g + 0.114 * b
            else:
                # 如果是颜色名称，使用默认亮度值
                brightness_map = {
                    '黑': 0, '深蓝': 50, '深绿': 50, '深红': 50, '深紫': 50,
                    '灰': 128, '棕': 100,
                    '蓝': 150, '绿': 150, '红': 150, '紫': 150,
                    '浅蓝': 200, '浅绿': 200, '粉': 220, '浅紫': 200,
                    '白': 255, '浅黄': 240, '黄': 220, '橙': 200
                }
                return brightness_map.get(color, 128)
        
        top_brightness = sum(get_brightness(c) for c in top_colors) / len(top_colors)
        bottom_brightness = sum(get_brightness(c) for c in bottom_colors) / len(bottom_colors)
        
        if top_brightness >= bottom_brightness:
            score = 100.0
            passed = True
            message = "符合上浅下深原则"
            suggestion = None
            severity = RuleSeverity.INFO
        else:
            diff = bottom_brightness - top_brightness
            score = max(0, 100 - diff / 2)
            passed = False
            message = f"违反上浅下深原则（上衣亮度: {top_brightness:.1f}, 下装亮度: {bottom_brightness:.1f}）"
            suggestion = "建议选择更浅的上衣颜色或更深的下装颜色"
            severity = RuleSeverity.WARNING
        
        return RuleResult(
            passed=passed,
            score=score,
            message=message,
            suggestion=suggestion,
            severity=severity,
            weight=self.weight
        )


class ForbiddenColorComboRule(ColorRule):
    """禁忌颜色组合规则：红绿、紫黄等互补色不能同时出现"""
    
    def __init__(self, weight: float = 1.8):
        super().__init__(
            name="禁忌颜色组合",
            description="避免互补色直接搭配（如红绿、紫黄）",
            weight=weight
        )
        # 定义禁忌组合
        self.forbidden_combos = [
            ({'红', '深红', '粉'}, {'绿', '深绿', '浅绿'}),
            ({'紫', '深紫', '浅紫'}, {'黄', '浅黄', '橙'}),
            ({'蓝', '深蓝', '浅蓝'}, {'橙', '黄', '浅黄'}),
        ]
    
    def _evaluate_colors(self, colors: List[Any], outfit_data: Dict[str, Any]) -> RuleResult:
        """评估禁忌颜色组合"""
        # 提取所有颜色名称
        color_names = []
        for color in colors:
            if isinstance(color, tuple):
                color_info = classify_color_type(color)
                color_names.append(color_info['name'])
            else:
                color_names.append(str(color))
        
        color_set = set(color_names)
        
        # 检查是否有禁忌组合
        violations = []
        for combo1, combo2 in self.forbidden_combos:
            has_combo1 = bool(color_set & combo1)
            has_combo2 = bool(color_set & combo2)
            
            if has_combo1 and has_combo2:
                combo1_name = ', '.join(combo1)
                combo2_name = ', '.join(combo2)
                violations.append(f"{combo1_name} 与 {combo2_name}")
        
        if not violations:
            score = 100.0
            passed = True
            message = "未发现禁忌颜色组合"
            suggestion = None
            severity = RuleSeverity.INFO
        else:
            score = 50.0
            passed = False
            message = f"发现禁忌颜色组合: {', '.join(violations)}"
            suggestion = "建议避免互补色直接搭配，可以使用中性色（黑/白/灰）作为过渡"
            severity = RuleSeverity.ERROR
        
        return RuleResult(
            passed=passed,
            score=score,
            message=message,
            suggestion=suggestion,
            severity=severity,
            weight=self.weight
        )


class StyleCoordinationRule(StyleRule):
    """款式协调规则：正装配正装鞋等"""
    
    def __init__(self, weight: float = 1.5):
        super().__init__(
            name="款式协调",
            description="上下装和鞋子的风格应该协调",
            weight=weight
        )
        # 定义风格分类
        self.formal_styles = {'衬衫', '外套', '皮鞋'}
        self.casual_styles = {'T恤', '卫衣', '牛仔裤', '休闲裤', '运动鞋'}
    
    def _evaluate_styles(self, styles: Dict[str, str], outfit_data: Dict[str, Any]) -> RuleResult:
        """评估款式协调"""
        top_style = styles.get('top', '')
        bottom_style = styles.get('bottom', '')
        shoe_style = styles.get('shoes', '')
        
        # 判断风格类型
        def get_style_type(style):
            if style in self.formal_styles:
                return 'formal'
            elif style in self.casual_styles:
                return 'casual'
            else:
                return 'unknown'
        
        top_type = get_style_type(top_style)
        bottom_type = get_style_type(bottom_style)
        shoe_type = get_style_type(shoe_style)
        
        # 统计风格类型
        types = [t for t in [top_type, bottom_type, shoe_type] if t != 'unknown']
        
        if not types:
            return RuleResult(
                passed=True,
                score=100.0,
                message="无法判断款式风格",
                severity=RuleSeverity.INFO,
                weight=self.weight
            )
        
        # 检查是否一致
        unique_types = set(types)
        
        if len(unique_types) == 1:
            score = 100.0
            passed = True
            message = "款式风格协调统一"
            suggestion = None
            severity = RuleSeverity.INFO
        elif len(unique_types) == 2:
            # 部分混合，可以接受
            score = 70.0
            passed = True
            message = "款式风格部分混合，基本协调"
            suggestion = "建议统一风格以获得更好的视觉效果"
            severity = RuleSeverity.WARNING
        else:
            # 风格混乱
            score = 40.0
            passed = False
            message = "款式风格不协调，正装与休闲混搭"
            suggestion = "建议统一风格：正装配正装，休闲装配休闲装"
            severity = RuleSeverity.ERROR
        
        return RuleResult(
            passed=passed,
            score=score,
            message=message,
            suggestion=suggestion,
            severity=severity,
            weight=self.weight
        )


class ContextAppropriateRule(ContextRule):
    """场景适宜规则：根据场景选择合适的穿搭"""
    
    def __init__(self, weight: float = 1.3):
        super().__init__(
            name="场景适宜",
            description="根据场景选择合适的穿搭风格",
            weight=weight
        )
        # 定义场景与风格的映射
        self.context_styles = {
            '正式场合': {'formal'},
            '商务': {'formal'},
            '工作': {'formal', 'casual'},
            '休闲': {'casual'},
            '运动': {'casual'},
            '聚会': {'casual', 'formal'},
        }
    
    def _evaluate_context(self, context: Dict[str, Any], outfit_data: Dict[str, Any]) -> RuleResult:
        """评估场景适宜性"""
        context_type = context.get('type', '')
        styles = outfit_data.get('styles', {})
        
        if not context_type:
            return RuleResult(
                passed=True,
                score=100.0,
                message="未指定场景类型",
                severity=RuleSeverity.INFO,
                weight=self.weight
            )
        
        # 获取场景推荐的风格
        recommended_styles = self.context_styles.get(context_type, set())
        
        if not recommended_styles:
            return RuleResult(
                passed=True,
                score=100.0,
                message=f"场景 '{context_type}' 无特定风格要求",
                severity=RuleSeverity.INFO,
                weight=self.weight
            )
        
        # 判断当前穿搭风格
        top_style = styles.get('top', '')
        bottom_style = styles.get('bottom', '')
        shoe_style = styles.get('shoes', '')
        
        formal_styles = {'衬衫', '外套', '皮鞋'}
        casual_styles = {'T恤', '卫衣', '牛仔裤', '休闲裤', '运动鞋'}
        
        current_formal = any(s in formal_styles for s in [top_style, bottom_style, shoe_style])
        current_casual = any(s in casual_styles for s in [top_style, bottom_style, shoe_style])
        
        # 判断是否匹配
        is_formal_ok = 'formal' in recommended_styles and current_formal
        is_casual_ok = 'casual' in recommended_styles and current_casual
        
        if is_formal_ok or is_casual_ok:
            score = 100.0
            passed = True
            message = f"穿搭风格适合{context_type}场景"
            suggestion = None
            severity = RuleSeverity.INFO
        else:
            score = 60.0
            passed = False
            if 'formal' in recommended_styles:
                message = f"{context_type}场景建议穿正装，当前穿搭过于休闲"
                suggestion = "建议选择衬衫、外套、皮鞋等正装单品"
            else:
                message = f"{context_type}场景建议穿休闲装，当前穿搭过于正式"
                suggestion = "建议选择T恤、牛仔裤、运动鞋等休闲单品"
            severity = RuleSeverity.WARNING
        
        return RuleResult(
            passed=passed,
            score=score,
            message=message,
            suggestion=suggestion,
            severity=severity,
            weight=self.weight
        )


# ==================== 规则库 ====================

class RuleLibrary:
    """规则库：管理所有规则"""
    
    def __init__(self):
        """初始化规则库，加载默认规则"""
        self.rules: List[BaseRule] = []
        self._load_default_rules()
    
    def _load_default_rules(self):
        """加载默认规则"""
        # 颜色规则
        self.rules.append(ThreeColorRule(max_colors=3, weight=1.5))
        self.rules.append(LightTopDarkBottomRule(weight=1.2))
        self.rules.append(ForbiddenColorComboRule(weight=1.8))
        
        # 款式规则
        self.rules.append(StyleCoordinationRule(weight=1.5))
        
        # 场景规则
        self.rules.append(ContextAppropriateRule(weight=1.3))
    
    def add_rule(self, rule: BaseRule):
        """添加规则"""
        self.rules.append(rule)
    
    def remove_rule(self, rule_name: str):
        """移除规则"""
        self.rules = [r for r in self.rules if r.name != rule_name]
    
    def get_rule(self, rule_name: str) -> Optional[BaseRule]:
        """获取指定规则"""
        for rule in self.rules:
            if rule.name == rule_name:
                return rule
        return None
    
    def enable_rule(self, rule_name: str):
        """启用规则"""
        rule = self.get_rule(rule_name)
        if rule:
            rule.enabled = True
    
    def disable_rule(self, rule_name: str):
        """禁用规则"""
        rule = self.get_rule(rule_name)
        if rule:
            rule.enabled = False
    
    def get_enabled_rules(self) -> List[BaseRule]:
        """获取所有启用的规则"""
        return [r for r in self.rules if r.enabled]


# ==================== 规则评估器 ====================

class RuleEvaluator:
    """规则评估器：评估穿搭是否符合规则"""
    
    def __init__(self, rule_library: Optional[RuleLibrary] = None):
        """
        初始化评估器
        
        参数:
            rule_library: 规则库，如果为None则创建默认规则库
        """
        self.rule_library = rule_library or RuleLibrary()
    
    def evaluate_outfit(self, 
                       colors: Optional[List[Any]] = None,
                       styles: Optional[Dict[str, str]] = None,
                       context: Optional[Dict[str, Any]] = None,
                       top_colors: Optional[List[Any]] = None,
                       bottom_colors: Optional[List[Any]] = None) -> Dict[str, Any]:
        """
        评估穿搭
        
        参数:
            colors: 整体颜色列表（RGB元组或颜色名称）
            styles: 款式字典，包含'top', 'bottom', 'shoes'等键
            context: 场景字典，包含'type'等键
            top_colors: 上衣颜色列表（可选）
            bottom_colors: 下装颜色列表（可选）
        
        返回:
            Dict包含:
                - score: 总体评分（0-100）
                - passed: 是否通过所有关键规则
                - results: 各规则评估结果列表
                - suggestions: 改进建议列表
                - summary: 评估摘要
        """
        # 构建穿搭数据
        outfit_data = {
            'colors': colors or [],
            'styles': styles or {},
            'context': context or {},
            'top_colors': top_colors or (colors or []),  # 如果没有单独指定，使用整体颜色
            'bottom_colors': bottom_colors or (colors or []),
        }
        
        # 评估所有启用的规则
        rule_results = []
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for rule in self.rule_library.get_enabled_rules():
            result = rule.evaluate(outfit_data)
            result.weight = rule.weight  # 确保权重正确
            rule_results.append({
                'rule_name': rule.name,
                'rule_description': rule.description,
                'passed': result.passed,
                'score': result.score,
                'message': result.message,
                'suggestion': result.suggestion,
                'severity': result.severity.value,
                'weight': result.weight
            })
            
            # 计算加权分数
            total_weighted_score += result.score * result.weight
            total_weight += result.weight
        
        # 计算总体评分
        overall_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
        
        # 收集建议
        suggestions = []
        error_count = 0
        warning_count = 0
        
        for result in rule_results:
            if result['suggestion']:
                suggestions.append({
                    'rule': result['rule_name'],
                    'suggestion': result['suggestion'],
                    'severity': result['severity']
                })
            
            if result['severity'] == 'error':
                error_count += 1
            elif result['severity'] == 'warning':
                warning_count += 1
        
        # 判断是否通过（没有严重错误）
        passed = error_count == 0
        
        # 生成摘要
        summary = {
            'total_rules': len(rule_results),
            'passed_rules': sum(1 for r in rule_results if r['passed']),
            'failed_rules': sum(1 for r in rule_results if not r['passed']),
            'errors': error_count,
            'warnings': warning_count
        }
        
        return {
            'score': round(overall_score, 2),
            'passed': passed,
            'results': rule_results,
            'suggestions': suggestions,
            'summary': summary
        }
    
    def add_custom_rule(self, rule: BaseRule):
        """添加自定义规则"""
        self.rule_library.add_rule(rule)
    
    def configure_rule(self, rule_name: str, weight: Optional[float] = None, enabled: Optional[bool] = None):
        """配置规则"""
        rule = self.rule_library.get_rule(rule_name)
        if rule:
            if weight is not None:
                rule.weight = weight
            if enabled is not None:
                rule.enabled = enabled


# ==================== 便捷函数 ====================

def create_evaluator() -> RuleEvaluator:
    """创建默认的规则评估器"""
    return RuleEvaluator()


def evaluate_outfit(colors: Optional[List[Any]] = None,
                   styles: Optional[Dict[str, str]] = None,
                   context: Optional[Dict[str, Any]] = None,
                   **kwargs) -> Dict[str, Any]:
    """
    便捷函数：评估穿搭
    
    参数:
        colors: 整体颜色列表
        styles: 款式字典
        context: 场景字典
        **kwargs: 其他参数（top_colors, bottom_colors等）
    
    返回:
        评估结果字典
    """
    evaluator = create_evaluator()
    return evaluator.evaluate_outfit(colors, styles, context, **kwargs)


# ==================== 使用示例 ====================

if __name__ == '__main__':
    print("=" * 60)
    print("穿搭规则引擎测试")
    print("=" * 60)
    
    # 创建评估器
    evaluator = create_evaluator()
    
    # 测试用例1：符合规则的穿搭
    print("\n【测试1】符合规则的穿搭")
    print("-" * 60)
    result1 = evaluator.evaluate_outfit(
        colors=[(255, 255, 255), (0, 0, 0), (100, 150, 200)],  # 白、黑、蓝
        styles={'top': '衬衫', 'bottom': '休闲裤', 'shoes': '皮鞋'},
        context={'type': '工作'}
    )
    print(f"总体评分: {result1['score']}")
    print(f"是否通过: {result1['passed']}")
    print(f"通过规则: {result1['summary']['passed_rules']}/{result1['summary']['total_rules']}")
    print("\n规则评估结果:")
    for r in result1['results']:
        status = "✓" if r['passed'] else "✗"
        print(f"  {status} {r['rule_name']:15} - {r['message']}")
    
    if result1['suggestions']:
        print("\n改进建议:")
        for s in result1['suggestions']:
            print(f"  - [{s['severity']}] {s['suggestion']}")
    
    # 测试用例2：违反规则的穿搭
    print("\n【测试2】违反规则的穿搭")
    print("-" * 60)
    result2 = evaluator.evaluate_outfit(
        colors=[(255, 0, 0), (0, 255, 0), (255, 255, 0), (0, 0, 255)],  # 红、绿、黄、蓝（4种颜色+红绿禁忌）
        styles={'top': 'T恤', 'bottom': '牛仔裤', 'shoes': '皮鞋'},  # 混搭
        context={'type': '正式场合'}  # 场景不匹配
    )
    print(f"总体评分: {result2['score']}")
    print(f"是否通过: {result2['passed']}")
    print(f"错误数: {result2['summary']['errors']}, 警告数: {result2['summary']['warnings']}")
    print("\n规则评估结果:")
    for r in result2['results']:
        status = "✓" if r['passed'] else "✗"
        print(f"  {status} {r['rule_name']:15} - {r['message']}")
    
    if result2['suggestions']:
        print("\n改进建议:")
        for s in result2['suggestions']:
            print(f"  - [{s['severity']}] {s['suggestion']}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

